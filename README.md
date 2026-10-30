# VOLPAROSSA — The Library of Tomorrow

The public website at **https://volparossa.org/**: a visual library homepage,
central documentation entrance and compact application directory. All visitor
content is English. Original application/Core code is unchanged.

## Build and preview

Python 3 is the only build dependency. Generated HTML is committed for the
existing GitHub Pages `main` / root publication source.

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. The site works without JavaScript. The check is
network-free and verifies pages, local links/fragments, metadata, semantic
structure, asset paths, the app registry, upstream attribution and byte budgets.
Use `--external-list` for a link inventory.

## Maintain

- `site/pages/`: semantic page bodies, including docs, applications and policies.
- `site/templates/`: shared head, navigation, footer and active states.
- `site/data/applications.json`: one app registry; unpublished sites link to GitHub.
- `assets/tokens.css`, `assets/site.css`, `assets/site.js`: design v1.0.2 and optional menu enhancement.
- `assets/library/`: responsive library imagery and mobile crops, generated from the approved references.
- `scripts/build_site.py`: deterministic standard-library generation.
- `scripts/export_theme.py`: versioned, self-contained theme export for future project repositories.

Run the build after editing sources and commit both sources and generated pages.
Keep `CNAME=volparossa.org`, `.nojekyll`, HTTPS and the existing Pages source.
No deployment workflow, DNS change, tracker, backend or cookie banner is added.

Read the [design decisions](docs/development/DESIGN.md),
[architecture and reuse](docs/development/ARCHITECTURE.md),
[asset/rights register](docs/development/ASSETS.md),
[content sources](docs/development/CONTENT.md) and
[verification report](docs/development/VERIFICATION.md).
Review renders are in [docs/review](docs/review).

## Content and publication boundaries

Applications remain development integrations or research. Dated trials retain
their exact-source scope; they do not establish a supported release, complete
private-storage maintenance or confidential peer computation. The linked Core
implementation ledger remains authoritative. No payment offer is created.

Public builds use text acknowledgements for unresolved Immich/OpenCloud logo
promotion. An isolated review build can show the original provided marks; see
the architecture note. Upstream screen excerpts are attributed examples, not
VOLPAROSSA integration evidence. No private user data is used.

The website is materially AI-assisted: code, copy and new environment artwork
were prepared with AI, then checked in real browsers. The original project
[GPL-3.0-only license](LICENSE) is unchanged. Fonts, upstream marks and interface
images retain separate notices and rights in the asset register.

The replaced prototype artwork originated in `VOLPAROSSA/.github` at
`3dd14afef7e7a1e08f6a46ae9424542a9400ae3d`, original SHA-256
`f9300dd5cd7c725905a11c43db6e855cb765e221b1f0e7e5a0db5218b2f23f27`.
It is no longer used; its original provenance remains recorded here and in Git.

## Optional browser QA

With Node.js 22.19+ and an installed browser, install the pinned development
utilities with `npm ci`. They are not shipped to visitors and are not needed
for static builds. Start the local server, then run:

```sh
CHROME_PATH=/usr/bin/chromium npm run qa
CHROME_PATH=/usr/bin/chromium npm run qa:scenes
```

Omit `CHROME_PATH` to use Playwright's separately installed Chromium. The checker
covers all eight rendered routes at 320, 390, 768, 1440 and 1920 pixels, axe at
mobile/desktop widths, keyboard/menu use, no JavaScript, reduced motion and
200% text enlargement. Results go to ignored `work/qa/`. Override `SITE_QA_URL`
and `SITE_QA_OUTPUT` when needed. Screenshot/accessibility capture expands
content-visibility regions so below-fold content is included in the inspection;
normal responsive checks retain the optimization.
