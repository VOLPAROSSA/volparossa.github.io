#!/usr/bin/env python3
"""Inert source checks only: no network, browser, package install or build."""
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
    def __init__(self):
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
        if tag in {"script", "iframe", "embed", "object", "form", "base"}:
            self.errors.append(f"Unexpected active or embedded content: {tag}")
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
        assert self.title.strip() == "VOLPAROSSA — A network built by all of us", "Unexpected or missing title"
        assert self.has_main and self.has_skip, "Missing main landmark or skip link"
        assert self.headings.count(1) == 1 and self.headings[0] == 1, "Expected one first-level heading"
        assert all(b <= a + 1 for a, b in zip(self.headings, self.headings[1:])), "Skipped heading level"
        assert not self.stack, f"Unclosed HTML: {self.stack}"
        for key in ("description", "viewport", "theme-color", "og:type", "og:title", "og:description", "og:url", "og:image", "og:image:alt", "og:image:width", "og:image:height", "twitter:card", "twitter:image", "twitter:image:alt"):
            assert self.metadata.get(key), f"Missing metadata: {key}"
        assert self.links.get("canonical") == ORIGIN + "/", "Canonical URL drift"
        assert self.metadata["og:url"] == ORIGIN + "/", "Social URL drift"
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
            local = (ROOT / unquote(parsed.path).lstrip("/")).resolve()
            assert local.is_relative_to(ROOT), f"Path escapes site: {value}"
            if local == ROOT:
                local = ROOT / "index.html"
            assert local.is_file(), f"Missing local target: {value}"
            if local == ROOT / "index.html" and parsed.fragment:
                assert unquote(parsed.fragment) in self.ids, f"Missing fragment: {value}"
        assert not self.errors, "\n".join(self.errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external-list", action="store_true", help="Print external link inventory without fetching")
    args = parser.parse_args()
    page = Page()
    page.feed((ROOT / "index.html").read_text())
    page.close()
    page.check()
    assert (ROOT / "CNAME").read_bytes() == b"volparossa.org", "Hosting CNAME changed"
    assert (ROOT / ".nojekyll").is_file(), "Missing static Pages marker"
    assert (ROOT / "LICENSE").is_file(), "Missing license"
    css = (ROOT / "assets/site.css").read_text()
    assert not re.search(r"@import|url\s*\(", css, re.I), "Unexpected CSS subresource"
    assert "prefers-reduced-motion: reduce" in css, "Missing reduced-motion treatment"
    assert ":focus-visible" in css and "forced-colors: active" in css, "Missing focus or forced-color treatment"
    ET.parse(ROOT / "assets/compass.svg")
    sitemap = ET.parse(ROOT / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    assert [node.text for node in sitemap.findall(".//s:loc", namespace)] == [ORIGIN + "/"], "Sitemap drift"
    assert f"Sitemap: {ORIGIN}/sitemap.xml" in (ROOT / "robots.txt").read_text()
    app_names = {"browser", "chat", "mail", "code", "image", "map", "weather", "cloud", "bank", "citizen"}
    assert all(f"https://github.com/VOLPAROSSA/volparossa-{name}" in page.external for name in app_names), "Missing application repository"
    assets = list((ROOT / "assets").iterdir())
    print(f"PASS: local targets/fragments, balanced HTML, {len(page.headings)} headings, {page.images} images, metadata, 10 application links, sitemap, CNAME and inert assets")
    print(f"Assets: {sum(path.stat().st_size for path in assets):,} bytes across {len(assets)} files")
    print(f"External links: {len(page.external)} inventoried; not fetched. These checks do not establish browser accessibility or network acceptance.")
    if args.external_list:
        print("\n".join(sorted(page.external)))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
