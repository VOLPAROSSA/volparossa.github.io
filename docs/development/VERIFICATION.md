# Website verification — 30 October 2026

## Desktop rendering correction (design 1.0.1)

The owner's 27-inch Firefox report exposed desktop hero cropping and independent
screen offsets. The hero now keeps its complete 3:2 image. A shared SVG coordinate
plane projects the complete interface images onto the measured device apertures
on desktop and the matching mobile crops. Application panels follow the stations
at wide sizes. The original Immich and OpenCloud marks are now present, with
attribution; the owner explicitly requested them in this correction. The asset
register records that choice separately from third-party permissions.

- `npm run qa:scenes`: 14 homepage checks in Chromium 154 and Firefox 153 at
  320, 390, 768, 1440, 1920, 2560 and 3840 CSS pixels, DPR 1. Full hero ratio,
  all three loaded interface images, no display cropping, all three visible
  marks and no horizontal overflow. Documentation and applications checked at
  2560; 200% desktop text resize and mobile navigation without JavaScript pass.
- `npm run qa`: the existing 40 route/width checks pass; all 16 axe scans report
  zero violations. Keyboard, mobile menu, 200% mobile text and reduced motion pass.
- Skip-link focus was rechecked in both browsers after replacing off-screen
  positioning with clipping; it is visible on focus and reaches main correctly.
- Actual full-page and worktable renders reviewed in both browsers, including
  2560 desktop and 390 mobile. The large Firefox scene was also inspected at
  3840. Artifacts: [current browser review](../review/README.md).
- Lighthouse 13.6, local Python server, default mobile simulation / desktop
  preset: performance **98 / 99**, accessibility **100 / 100**, best practices
  **100 / 100**, SEO **100 / 100**. Mobile transfer **246 KiB**. These are lab
  measurements, not field Core Web Vitals. [Recorded metrics](../review/scene-performance.json).
- Build, static checks, original-logo hashes, text-only attribution variant,
  shared theme export (v1.0.1) and `git diff --check` pass. The new official
  screenshot downloads match their Git blob IDs in the asset register.
- WebKit remains unavailable because of the host libraries listed below; no
  Safari or physical 27-inch monitor result is claimed. Viewport dimensions,
  rather than screen diagonal, determine these responsive layouts.

The lazy-image check scrolls each image into view and waits for decoding before
checking it. An initial fast synthetic scroll left one Firefox 3840 image pending;
the per-image check and a slower real render both load it correctly.

## Original build verification

The following records the initial build. The correction results above supersede
its previous text-only brand decision and screenshot crops.

## Source and configuration

- `python3 scripts/build_site.py` generates all nine HTML pages using Python's standard library.
- `python3 scripts/check_site.py` passes: English language, one h1, heading order, balanced HTML, unique IDs, local links and fragments, dimensions/alt attributes, metadata/canonicals, local resources, sitemap, 11 app destinations, upstream attribution, root and nested asset paths, unchanged CNAME and license.
- `git diff --check` passes. The original V-and-fox source and retained copy have identical pixels and alpha.
- Existing Pages remains `legacy`, source `main:/`, domain `volparossa.org`, HTTPS enforced. No DNS, protection, deployment-source or other repository code change.
- External HEAD checks: 52 of 53 destinations returned 200 before publication. The new asset-register link on `main` returned the expected pre-merge 404; it must be confirmed after publication. Original Code/Image/Cloud project-site routes returned 404, so CTAs correctly select existing repositories.

## Real browser and accessibility checks

Chromium **154.0.8037.57**, Playwright **1.62.1**, Linux, DPR 1:

- Eight pages × **320, 390, 768, 1440 and 1920** CSS pixels: 40 route/width checks, no horizontal overflow, missing visible images, request failures or browser exceptions.
- axe-core/Playwright **4.14.0**, WCAG 2/2.1/2.2 A/AA tags, eight pages at 390 and 1440: **zero detected violations** in 16 scans. Off-screen content is expanded for scans.
- Skip link is first focusable action and reaches main; mobile details menu, Escape/focus return and documentation navigation pass.
- Native menu and application content work with JavaScript disabled.
- Shared-strength anchor reaches the rendered target; reduced-motion uses native instant scrolling and disables optional transitions.
- **200% text enlargement** at 390 pixels passes without overflow. This exposed and fixed navigation, card and layer-grid intrinsic sizing. It is text resize, not a claim of testing every device/browser zoom implementation.
- An exported, self-contained design sample under `/volparossa-example/` loads local CSS, JS, fonts and images with no failed requests. The committed nested example is also in the route matrix.

Firefox **153.0**: home, documentation and applications at 390/1440, no overflow,
missing images or console errors; native mobile navigation passes. WebKit 26.5
was downloaded but could not launch: this host lacks GTK4, Graphene,
Harfbuzz-ICU, libmanette, libhyphen and GLESv2. No Safari success is claimed.
No physical phone, independent screen-reader audit or full WCAG certification.

## Visual comparison and corrections

Reviewed real full desktop/mobile renders and the worktable detail against both
supplied references. Reference 02 controls the continuous three-station table,
heading placement and device/panel relationships. Corrected screen coordinates,
hero framing, missing Unicode glyphs, mobile text reflow and final title placement.
Generated a dedicated portrait hero to retain the central arch and fox.

The shared reading table and closing fox balcony are separate sharp images.
The initial Image/Cloud labels used a text fallback, superseded by the
owner-requested original marks in design 1.0.1. The Image screen now uses the
complete official tag-view example, rather than the previous thin crop. On mobile the stations stack in DOM order, each
with its own image crop, description, status and working destination.
Full-page captures first load all images and expand native off-screen rendering;
they do not substitute concept art for browser output. See [review images](../review/README.md).

## Performance lab

Lighthouse **13.6.0**, fresh Chromium profiles against the Python HTTP server on
loopback, default simulated mobile throttling / desktop preset. The server has
no compression or cache headers; production GitHub Pages delivery may differ.
No field Core Web Vitals, real-user performance or supported application runtime
claim is inferred from these lab checks.

| Preset | Performance | Accessibility | Best practices | SEO | LCP | TBT | CLS | Transferred |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Mobile | 98 | 100 | 100 | 100 | 2.3 s | 20 ms | 0.001 | 237 KiB |
| Desktop | 99 | 100 | 100 | 100 | 0.9 s | 0 ms | 0.003 | 924 KiB |

[Mobile lab summary](../review/lighthouse-mobile.json) · [Desktop lab summary](../review/lighthouse-desktop.json). Full local reports accompany the summaries.

The mobile hero is **125,733 bytes AVIF**, **204,000 bytes WebP**, with JPEG
fallback. Desktop hero AVIF is **220,215 bytes** (WebP 385,630). Gzipped CSS and
JS together are **6,883 bytes**; the original approximately 150 kB target is met.
Only the hero is eager/high priority. Subsequent scenes/screens are lazy, with
native content-visibility reducing off-screen layout and decoding. Fonts, scripts,
images and icons are local; no third-party runtime requests, tracking or embeds.

The first unoptimized local pass scored 85 mobile performance. The recorded
improvement comes from the smaller AVIF hero and deferred off-screen rendering,
while retaining full WebP/JPEG imagery and no-JavaScript content.

## Reproduce

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1
# In another terminal, optional browser QA dependencies:
npm ci
CHROME_PATH=/usr/bin/chromium npm run qa
CHROME_PATH=/usr/bin/chromium npx lighthouse http://127.0.0.1:8000/ --chrome-flags='--headless --no-sandbox' --only-categories=performance,accessibility,best-practices,seo
```

The optional Node dependencies are development-only. No package manager,
JavaScript framework or backend is required to build or host production.
