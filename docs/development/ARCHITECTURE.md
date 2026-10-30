# Static publishing and shared design v1.0.3

`site/pages/` contains page bodies. `site/templates/` owns the common HTML head,
navigation and footer. `site/data/applications.json` is the single application
registry: name, repository, intended publication URL, publication flag, status,
upstream and description. `scripts/build_site.py` produces committed HTML. There
is no framework, runtime templating, database or package install for production.

Run `python3 scripts/build_site.py`, then `python3 scripts/check_site.py`.
The generated pages are served directly by the existing GitHub Pages source:
`main`, `/`, custom domain `volparossa.org`. CNAME and HTTPS settings are unchanged.
The public output includes the original upstream marks, as requested by the owner
in the desktop-render correction. Attribution and the conditions for future use
remain in the asset register. A text-only variant remains available for contexts
that require it:

```sh
python3 scripts/build_site.py --output work/text-brands --text-brands
```

Desktop hero height follows the intrinsic image ratio. Worktable screen apertures
are measured once in `SCREENS` in `scripts/build_site.py`. An SVG viewBox scales
that coordinate plane together with the source photo; mobile viewBoxes match the
three photo crops. CSS projection maps each complete interface image onto its
four aperture corners without visitor JavaScript. `object-fit: contain` keeps
all screenshot content visible. Keep the source crop and viewBox synchronized
when replacing artwork. Do not restore independent viewport-percentage offsets.

The shared status component renders as a bordered pill on the homepage and
application index, with a dark variant in the hero. Upstream logo slots preserve
the supplied SVG proportions and clear space. The GitHub mark is embedded from
`assets/icons/github.svg`; its MIT notice travels with the exported design.
The final section displays the existing chapter artwork across 64% of the desktop
section, feathered into the paper background with a CSS mask. At 800px and below,
it stacks beneath the copy with a vertical fade; both versions remain static and
respect text reflow.

## Independent application repositories

Future project sites use `/volparossa-code/`, `/volparossa-image/`, etc. Their
repository name remains in the path. `/code/` is not an automatic route.
The registry's `published` flag selects the project website or its GitHub
repository. Set that flag only after verifying the production project site.
Cloud was published on 30 October 2026 at
`https://volparossa.org/volparossa-cloud/` by
[Pages run 41131005030](https://github.com/VOLPAROSSA/volparossa-cloud/actions/runs/41131005030).
Its live HTML and assets matched the production build in Chromium and Firefox,
including mobile and 2560px desktop checks. Cloud's CTAs now open that site;
the application directory also retains a separate source-repository link.
Code and Image remain unpublished and their CTAs use their GitHub repositories.

The reusable example at `examples/volparossa-application/` exercises nested asset
paths. To bootstrap a genuinely independent site with its own asset directory:

```sh
python3 scripts/export_theme.py --output /tmp/theme-preview/volparossa-example
python3 -m http.server 8002 --bind 127.0.0.1 --directory /tmp/theme-preview
# Open http://127.0.0.1:8002/volparossa-example/
```

The exporter requires a clean committed source and records its exact Git SHA.
It copies versioned tokens, CSS, JS, local fonts/notices, original logo/favicon,
upstream marks and notices, head/header/footer sources, central navigation and
project/application data, and the shared navigation renderer. It emits a SHA-256
manifest. Use `--source-only` to omit the example and library social image when
vendoring a project's own page. See [the shared theme contract](../../site/shared-theme.md).
Copy from an exact reviewed website commit (or a future version tag), record
that commit in the consumer repository and commit the copied files there.
Updates are explicit vendor-update PRs. There is no runtime fetch from a moving
main branch. Retain the relative `assets/...` paths; set the new title, content,
canonical, metadata, application active state and sitemap before publication.
The example stays `noindex` until replaced with the real application content.

## Core project and central navigation

`site/data/navigation.json` and `scripts/shared_navigation.py` define the shared
header and footer. The Core project imports these exact files with the theme,
sets `active='core'`, and overrides only its own canonical and GitHub repository.
Its logo and general Documentation/Get involved links return to the homepage.
Social-image metadata is supplied by each site's builder through the shared
layout, so a Core page can use its harbour image without forking the head.

`site/data/projects.json` selects the Core destination. The flag is now enabled
after `https://volparossa.org/volparossa/` was successfully published and verified.
An unpublished project uses its real repository destination. The Core repository
owns its own Pages output; no local copy of its page is needed here.
The homepage's CNAME, publication source and root content remain unchanged.

`/docs/#core` and `/docs/#dps` are real central portal anchors. They link to the
maintained architecture/privacy and DPS source documents with “View on GitHub”.
DPS is a shared service in research and development, not a sixth Core layer or a
released positioning guarantee.

## Central documentation later

`/docs/` is a curated entry point, not a second copy of the technical manuals.
The owning repositories remain authoritative. All external guide destinations
are marked GitHub. A future rendering pipeline can read a manifest of repository,
exact commit, source path, license and canonical route; resolve relative links
at build time; then atomically publish one static snapshot. A build-time search
index can be generated from those rendered documents, versioned with the same
snapshot and loaded locally on demand. Do not label a link filter as full-text
search, or index private sources. No search control is shipped in this phase.

## Progressive enhancement and assets

The native `details` menu works without JavaScript. The optional script adds
Escape, closes after selection and closes on outside click. No stored state,
tracking or remote calls. Motion is limited to short hover/focus transitions
and smooth anchor navigation, disabled for reduced motion; no perpetual motion
needs a pause control.

Off-screen regions use native CSS content-visibility with intrinsic-size hints,
reducing initial layout/decoding without removing content or requiring scripts.
Hero AVIF has WebP and JPEG fallbacks.

The worktable is separate scenery, device-screen images and semantic application
cards. Desktop screen coordinates follow its 1536×710 image. On mobile each
article includes a device-centred crop before its text, without changing DOM
order. Scenery is decorative; the equivalent purpose, basis and status are HTML.
