# The Library of Tomorrow — design decision, 30 October 2026

The supplied `01-homepage-library-reference.png` governs the monumental library
hero, walnut/brass/ivory materials, shared reading table and closing fox balcony.
`02-applications-worktable-FINAL.png` **supersedes the entire applications section**:
one continuous worktable, Code left, Image centre, Cloud right. No niches, book
covers or giant horizontal app panels. The original V-and-fox mark is preserved.

Sequence: hero → worktable → shared Core and five layers → three dated,
source-bound milestones → invitation. The two worktable headings are verbatim.
Fonts: locally hosted Cormorant Garamond 400 and Inter 400, with OFL notices.
Text and controls are semantic HTML. Separate responsive scenery and upstream
interface images carry the visual composition. Narrow layouts retain each device
next to its description; native scrolling and no-JavaScript navigation remain.

Implementation: Python standard-library static generation, committed output,
shared header/footer, relative assets, one applications JSON file. Existing
main/root GitHub Pages source, CNAME, HTTPS and GPL license are preserved.

Execution: inspect sources and references; prepare individual images; implement
home/portals and reusable layout; check paths, render desktop/mobile and refine;
record performance/accessibility and publish through a reviewable PR. The user's
explicit request to replace production overrides the attachment's older
review-only publication instruction. No other repository code is modified.
