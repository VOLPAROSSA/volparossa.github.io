#!/usr/bin/env python3
"""Static semantic, path, metadata, asset and publication checks; no network."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://volparossa.org"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self, path):
        self.path = path
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.external = set()
        self.metadata = {}
        self.links = {}
        self.headings = []
        self.stack = []
        self.errors = []
        self.title = ""
        self.lang = None
        self.images = 0
        self.has_main = False
        self.has_skip = False

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "main":
            self.has_main = True
        if tag in {"iframe", "embed", "object", "form", "base"}:
            self.errors.append(f"Unexpected active or embedded content: {tag}")
        if tag == "script" and (attrs.get("src") != ("https://volparossa.org/assets/site.js" if self.path.name == "404.html" else "../" * len(self.path.relative_to(ROOT).parts[:-1]) + "assets/site.js") or "defer" not in attrs):
            self.errors.append("Unexpected script; only local deferred enhancement is allowed")
        if any(name.startswith("on") for name in attrs):
            self.errors.append("Inline event handler")
        identifier = attrs.get("id")
        if identifier:
            if identifier in self.ids:
                self.errors.append(f"Duplicate ID: {identifier}")
            self.ids.add(identifier)
        if tag == "meta":
            key = attrs.get("name", attrs.get("property"))
            if key:
                if key in self.metadata:
                    self.errors.append(f"Duplicate metadata: {key}")
                self.metadata[key] = attrs.get("content", "")
        if tag == "link":
            self.links[attrs.get("rel")] = attrs.get("href")
        if tag == "a" and "skip-link" in attrs.get("class", "").split():
            self.has_skip = attrs.get("href") == "#main"
        if tag == "img":
            self.images += 1
            if "alt" not in attrs:
                self.errors.append("Image has no alt attribute")
            if not attrs.get("width") or not attrs.get("height"):
                self.errors.append("Image has no intrinsic dimensions")
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        for name in ("href", "src"):
            if name in attrs:
                self.references.append((tag, name, attrs[name]))
        for candidate in attrs.get("srcset", "").split(","):
            if candidate.strip():
                self.references.append((tag, "srcset", candidate.strip().split()[0]))
        for ref in attrs.get("aria-labelledby", "").split():
            self.references.append((tag, "aria-labelledby", "#" + ref))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unbalanced HTML end tag: {tag}")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] == "title":
            self.title += data

    def check(self):
        assert self.lang == "en", "Missing page language"
        assert "VOLPAROSSA" in self.title and len(self.title.strip()) > 15, "Missing descriptive title"
        assert self.has_main and self.has_skip, "Missing main landmark or skip link"
        assert self.headings.count(1) == 1 and self.headings[0] == 1, "Expected one first-level heading"
        assert all(b <= a + 1 for a, b in zip(self.headings, self.headings[1:])), "Skipped heading level"
        assert not self.stack, f"Unclosed HTML: {self.stack}"
        for key in ("description", "viewport", "theme-color", "og:type", "og:title", "og:description", "og:url", "og:image", "og:image:alt", "og:image:width", "og:image:height", "twitter:card", "twitter:image", "twitter:image:alt"):
            assert self.metadata.get(key), f"Missing metadata: {key}"
        relative = self.path.relative_to(ROOT).as_posix()
        canonical = ORIGIN + "/" + relative.removesuffix("index.html")
        assert self.links.get("canonical") == canonical, "Canonical URL drift"
        assert self.metadata["og:url"] == canonical, "Social URL drift"
        assert self.metadata["twitter:card"] == "summary_large_image"
        for key in ("og:image", "twitter:image"):
            self.references.append(("meta", "content", self.metadata[key]))
        for tag, attribute, value in self.references:
            parsed = urlsplit(value)
            assert parsed.scheme in {"", "https"}, f"Unsafe or insecure URL: {value}"
            assert not parsed.netloc or parsed.scheme == "https", f"Protocol-relative URL: {value}"
            if parsed.netloc and parsed.netloc != "volparossa.org":
                assert tag == "a", f"External subresource: {value}"
                self.external.add(value)
                continue
            local = ((ROOT / unquote(parsed.path).lstrip("/")) if parsed.netloc or parsed.path.startswith("/") else (self.path.parent / unquote(parsed.path))).resolve()
            if not parsed.path:
                local = self.path
            assert local.is_relative_to(ROOT), f"Path escapes site: {value}"
            if local.is_dir():
                local = local / "index.html"
            assert local.is_file(), f"Missing local target: {value}"
            if local.suffix == ".html" and parsed.fragment:
                target = Page(local)
                target.feed(local.read_text())
                assert unquote(parsed.fragment) in target.ids, f"Missing fragment: {value}"
        assert not self.errors, "\n".join(self.errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external-list", action="store_true", help="Print external link inventory without fetching")
    args = parser.parse_args()
    from build_site import PAGES
    pages = []
    for route in PAGES:
        path = ROOT / (route if route.endswith(".html") else route + "index.html")
        page = Page(path)
        page.feed(path.read_text())
        page.close()
        page.check()
        pages.append(page)
    assert (ROOT / "CNAME").read_bytes() == b"volparossa.org", "Hosting CNAME changed"
    assert (ROOT / ".nojekyll").is_file(), "Missing static Pages marker"
    assert (ROOT / "LICENSE").is_file(), "Missing license"
    css = (ROOT / "assets/site.css").read_text()
    assert not re.search(r"@import", css, re.I), "Unexpected CSS import"
    for url in re.findall(r"url\(['\"]?([^)'\"]+)", css):
        assert not url.startswith(("http:", "https:", "//", "/")), f"Nonlocal CSS resource: {url}"
        assert (ROOT / "assets" / url).is_file(), f"Missing CSS resource: {url}"
    assert "prefers-reduced-motion:reduce" in css or "prefers-reduced-motion: reduce" in css, "Missing reduced-motion treatment"
    assert ":focus-visible" in css and "forced-colors:active" in css, "Missing focus or forced-color treatment"
    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    expected = [ORIGIN + "/" + r for r in PAGES if r not in ("404.html", "examples/volparossa-application/")]
    assert [node.text for node in sitemap.findall(".//s:loc", namespace)] == expected, "Sitemap drift"
    assert f"Sitemap: {ORIGIN}/sitemap.xml" in (ROOT / "robots.txt").read_text()
    import json, gzip
    apps = json.loads((ROOT / "site/data/applications.json").read_text())
    external = set().union(*(p.external for p in pages))
    assert len(apps) == len({a["id"] for a in apps}), "Duplicate app"
    assert all(a["repository"] in external for a in apps), "Missing app destination"
    assert all(not a["published"] or a["publication_url"].startswith(ORIGIN + "/volparossa-") for a in apps), "Invalid project-site path"
    home = (ROOT / "index.html").read_text()
    for text in ["Knowledge grows", "Familiar tools. New possibilities.", "Built on open source. Extended by VOLPAROSSA.", "Integration in development"]:
        assert text in home, f"Required content missing: {text}"
    for mark in ('opencode', 'immich', 'opencloud'):
        assert f'src="assets/upstream/{mark}.svg"' in home, f"Missing upstream mark: {mark}"
    assert not re.search(r'(?:href|src)="/assets/', (ROOT / "examples/volparossa-application/index.html").read_text()), "Root-absolute example asset"
    compressed = sum(len(gzip.compress((ROOT / "assets" / n).read_bytes())) for n in ("site.css", "site.js"))
    assert compressed < 150000, f"CSS/JS budget exceeded: {compressed}"
    assets = [p for p in (ROOT / "assets").rglob("*") if p.is_file()]
    print(f"PASS: {len(pages)} pages; local links/fragments, HTML, headings, metadata, {len(apps)} apps, source boundaries, sitemap, CNAME, local CSS/JS and subpath example")
    print(f"CSS/JS gzip: {compressed:,} bytes. Shipped asset variants: {sum(p.stat().st_size for p in assets):,} bytes across {len(assets)} files.")
    print(f"External links: {len(external)} inventoried; no network access performed.")
    if args.external_list:
        print("\n".join(sorted(external)))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
