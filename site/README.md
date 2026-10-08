# Learning site

Three static pages introduce the lab, adapt all seven teaching slides into
readable HTML, and present the complete workshop. The browser slides reflow;
the PDF preserves the original deck design. Editable PowerPoint remains a download.

Build with `python scripts/build_learning_site.py`. Serve `_site/` with
`python -m http.server 8765 --directory _site`. The builder needs only Python's
standard library, regenerates the workshop from `docs/workshop.md`, and checks
local destinations and fragments. The site has no analytics, forms, paid calls,
or browser execution of the lab. Exercises run in the learner's local checkout.

## Publishing

Before merging the learning-site PR, open repository **Settings → Pages** and
set **Source** to **GitHub Actions**. The GitHub connector cannot change this
administrative setting. The Learning site workflow verifies the pages on pull
requests, uploads a review artifact, and deploys only main after merge or an
explicit main-branch dispatch. Lab acceptance remains a separate required check.

Expected production base: https://bg-playground.github.io/rules-and-purpose-lab/

Verify introduction, slides, workshop, PDF, and PowerPoint on the published site
before merging the separate BradGuiderHome link update.

## Content maintenance

The workshop comes from its existing Markdown. Browser slide copy is in
`scripts/build_learning_site.py`; update it when the seven-slide source changes.
The PDF is an export of the matching PowerPoint in `docs/presentation/`. Re-export
and visually review every PDF page after deck edits. The web cover uses an
optimized derivative of the existing artwork; provenance is in `assets/README.md`.
Authored fixtures, simulated grading, scenario-only eligibility, and pending
teaching validation remain explicit. Site CI is not model-quality evidence.
