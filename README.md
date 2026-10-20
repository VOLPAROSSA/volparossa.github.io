# VOLPAROSSA public website

The public entry point at **https://volparossa.org/**. This is a buildless,
responsive HTML/CSS site for the project's purpose, five shared layers,
application family and source-bound development evidence. It has no JavaScript,
package manager, remote fonts, analytics or third-party embeds.

## Preview and check

From this repository, with Python 3 available:

```sh
python3 scripts/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. Use HTTP even for local preview because asset links
are root-relative. Stop the server with Ctrl-C. The check script does not fetch
links, start services, install tools, or modify anything. To inspect its external
link inventory, use `python3 scripts/check_site.py --external-list`.

Check the rendered page at narrow mobile (320 and 390 CSS pixels), tablet and
desktop widths. Check keyboard navigation, the skip link and visible focus,
200% text zoom, contrast, reduced motion and forced-color settings. All content
and links work without JavaScript. These source checks and manual checks are
not a WCAG conformance audit, real-device coverage or product runtime evidence.
Disposable profiles, logs and preview screenshots can live in ignored `.preview/`.

## Maintain the content

- `index.html`: content and semantic structure. Keep one `h1`, descriptive links,
  a usable skip link, image alternatives, explicit dimensions and heading order.
- `assets/site.css`: responsive layout, system fonts, visible focus, reduced
  motion, forced-color support and print treatment. No build step.
- `assets/compass.svg`: small original geometric compass favicon and site mark.
- `assets/gathering-800.jpg`, `assets/gathering-1600.jpg`: responsive brand artwork.
- `assets/social.jpg`: 1200 × 600 social preview. Keep Open Graph and card metadata
  aligned with this asset, the title, description and canonical production URL.
- `robots.txt`, `sitemap.xml`: discovery metadata. Update `lastmod` when changing
  public content. `CNAME` remains `volparossa.org`; `.nojekyll` serves the tree as
  plain static files. Preserve existing Pages configuration, custom domain,
  HTTPS enforcement and DNS. This repository adds no deployment workflow.

Use the [complete agreed goal](https://github.com/VOLPAROSSA/volparossa/blob/main/docs/development/GOAL.md)
and [current evidence ledger](https://github.com/VOLPAROSSA/volparossa/blob/main/docs/IMPLEMENTATION_STATUS.md#current-integration-and-active-work)
as the authorities. This page is a **20 October 2026 snapshot**, not a second
execution plan. Update its date only after reviewing current source and original
results. Keep scoped demonstrations, research, failed trials, and goals distinct.
Link the original evidence and its exact-source record; a later passing source
check does not replace a failed application or confidential-computing trial.
Do not imply a supported release, completed applications, privacy guarantees,
financial authorization, real-person voting or measured efficiency gains.

Keep shared contribution, support, conduct and accessibility guidance in
[VOLPAROSSA/.github](https://github.com/VOLPAROSSA/.github), rather than duplicating
it here. Funding information belongs in the core's
[public supporting guide](https://github.com/VOLPAROSSA/volparossa/blob/main/docs/community/SUPPORTING.md).
Sponsorship is pending; do not add a payment endpoint without independently
confirmed public authorization. Contribution to the network is not a payment.

External links are ordinary navigation, not embedded connections. Visitors make
hosting requests to GitHub Pages, which has its own request logging and privacy
policy. Do not describe an absence of site-added analytics as an absence of all
hosting logs. There is currently no cookie consent interface because the site
adds no cookies or tracking services.

## Artwork provenance and license

The existing VOLPAROSSA organization artwork was copied from
`VOLPAROSSA/.github`, `profile/assets/banner_volparossa.png`, source revision
`3dd14afef7e7a1e08f6a46ae9424542a9400ae3d` (inspected local clone).
Source dimensions: 1774 × 887; source SHA-256:
`f9300dd5cd7c725905a11c43db6e855cb765e221b1f0e7e5a0db5218b2f23f27`.
The artwork shows a wolf, compass map, lanterns and a shared worktable with the
VOLPAROSSA wordmark. It was reused, not newly generated for this website.

The three JPEG derivatives preserve the composition. They were scaled with the
already-available GdkPixbuf library, using bilinear interpolation: 1600 × 800
(JPEG quality 88), 800 × 400 (quality 85), and 1200 × 600 (quality 88). No tools
were installed. The original 3 MB PNG is not shipped to visitors. The responsive
hero is approximately 108 KB on small screens or 410 KB at its larger size;
the separate social asset is approximately 255 KB. The precise byte inventory is
printed by the local check. Preserve the upstream artwork's provenance when
replacing or redistributing it.

The original repository [GPL-3.0-only license](LICENSE) is preserved. Application
names identify independent integrations; they do not imply upstream endorsement
and do not change the applications' own licenses and notices.
