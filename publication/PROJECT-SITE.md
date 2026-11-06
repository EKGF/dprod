# DPROD project website

The five public project pages are authored in `project-site/*.md`; their
publication definition is `project-site.ttl`. GraphArch generates static HTML,
CSS and small navigation scripts. The content repo does not need JSX, React,
Tailwind, or a JavaScript application build to generate these pages.

```sh
python scripts/central_publications.py \
  --manifest publication/publications.json \
  --grapharch /path/to/the/pinned/grapharch \
  --output output/central-publications
```

`publications.json` on the leading branch owns the selected refs, labels,
publication status, path prefixes and one exact GraphArch revision. The leading
branch is `develop` here; the manifest can choose another branch for another
project. GitHub discovery needs repository pull-request read access; it never
queries Vercel. Rendering does not receive that credential.

Every selected source is rebuilt using that one engine. The website, each
specification, its PDFs and its native data artifacts are assembled into one
portable static tree. A missing source definition, invalid branch, failed
render, path collision or failed assembly aborts the whole publication. Nothing
is deployed from a partial build, and no previous deployed directory is an input.

The EKGF project layout uses source-owned Markdown/frontmatter for section
composition. Branding and reusable rendering belong to GraphArch, not JSX,
React, Tailwind or project-specific templates in this repository.

## Source and parity

The initial content was transcribed from the current public project pages on
2 November 2026, backed by this repository's `site/src/app/` pages (source revision
`1979af85577492a1e022f30fbe1b010c837d5b29`). Page text, links, lists and code
examples are retained. JSON and citation fences have explicit language metadata;
timeline status/date separators and the community contact link are normalized.
The source Next.js files remain in place until the pilot is reviewed.

The source-owned pages include home, why, concepts, adopt and roadmap. The
central build resolves selected branch and PR heads once, records their exact
SHAs, and contributes a publication inventory to the website's graph. The
specification-version page links to local directories in this assembled site.
Main is **DPROD 1.0 beta**; develop and PRs are explicitly unstandardized drafts.
No approval status is inferred from a Git branch name.

The manifest selects main and develop and currently includes open human PRs
from this repository, excluding dependabot branches and forks. PR numbers give
stable collision-free paths such as `spec/pr-234/`. Explicit long-lived branches
can be added to `publications`; sources lacking publication definitions need
tracked publication-only maintenance, not a fallback to develop content.

Frontmatter descriptions retain the current project's search descriptions. The
website target supplies the public canonical base, `https://ekgf.org/dprod/`;
GraphArch generates canonical/Open Graph metadata, a sitemap and robots file.
Preview deployments intentionally keep those production canonical URLs.

## Workflow and provenance

`.github/workflows/grapharch-pdfs.yml` runs the orchestrator from trusted
`develop`, including when another ref triggered it. It runs on develop pushes,
PR lifecycle events, completion of existing source-validation workflows, manual
requests and an hourly refresh. Selected source branches are read as Git blobs;
their build scripts, Python, JavaScript and dependency manifests are never run.
A separate deployment job receives Vercel credentials only after a complete
assembly artifact exists. Fork PRs are not published by the current manifest.

The build retains each source's exported documentation KG and target manifests,
plus a `publication-build.json` recording the source SHAs, leading configuration
SHA, selected generator revision and executable checksum. Resource serialization
uses the trusted leading-branch serializer with each source's ontology namespace;
it does not fetch ontology imports. Original RDF files are retained byte for
byte alongside derived JSON-LD/RDF/XML forms.

Updating the single GraphArch pin deliberately rerenders all selected sources.
Historical source semantics are not rewritten or renamed. Rebuilds produce a
new build record; this workflow does not claim byte-identical historical HTML or
that a freshly generated old-source publication is an approved new standard.

## Hosting and migration boundary

The complete package is
`output/central-publications/deployment/.vercel/output/`. Its `static/` tree is
portable to static hosts; `config.json` holds Vercel routes and RDF media types.
Custom mounts belong in the manifest and must agree with the canonical base URL.

The `/dprod/` mount matches the EKGF website proxy. `/dprod/spec/` selects develop;
`/dprod/spec/main/` selects 1.0 beta and `/dprod/spec/develop/` selects the current
working draft. Stable entry URLs open each bundle's `specification/` target,
keeping target-relative PDF and asset links intact. `/dprod/spec/archive/1.0/`
is retained as an alias for the main-source build; it is no longer described as
a frozen approved release. The contracts profile IRIs return native Turtle.
Selected PR directories are fully included locally, with no remote deployment
redirects. Closing a PR removes it from the next assembled site's inventory.

CI deploys a reviewable preview; it does not promote it to production. The
existing production Next.js publication remains until a separately verified
cutover. Its Git integration and legacy PR domain workflow must be retired when
that cutover happens, so only one publisher owns production. Root-domain sitemap
integration and the branded 404 page remain separate work.

## Independent GitHub Pages review site

`.github/workflows/grapharch-pages.yml` publishes the same complete selected-source
assembly at <https://ekgf.github.io/dprod/>. It uses the GraphArch composite action
in source-revision install mode, pinned by `publications.json`; no branch or PR
build code runs. `github-pages.json` supplies only hosting metadata. The existing
ReSpec and Vercel workflows remain active in parallel, with no production cutover.

The Pages upload contains the contents of the mounted `static/dprod` directory:
GitHub supplies `/dprod/`, so it must not be nested a second time. The generated
website canonical URL and version inventory use the Pages hostname. Normative
ontology IRIs and source specification identities remain unchanged. `.nojekyll`
is present and `CNAME` is forbidden; this site uses the default Pages domain.

Pages cannot apply Vercel's custom response headers or file-alias routing. RDF
artifacts remain available through their explicit `.ttl`, `.jsonld`, and `.rdf`
URLs. Canonical profile IRIs still identify the original published RDF resources.
The workflow verifies the deployed configuration revision and all selected
specification routes before succeeding.
