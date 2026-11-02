# DPROD project website

The five public project pages are authored in `project-site/*.md`; their
publication definition is `project-site.ttl`. GraphArch generates static HTML,
CSS and small navigation scripts. The content repo does not need JSX, React,
Tailwind, or a JavaScript application build to generate these pages.

```sh
grapharch publication build-site \
  --source publication/project-site \
  --definitions publication/project-site.ttl \
  --project urn:dprod:project-site \
  --target urn:dprod:project-site:website \
  --output-root output/grapharch-project-site
```

The build-time version inventory requires `GITHUB_TOKEN` (repository pull-request
read access), `VERCEL_TOKEN`, `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID`. CI provides
these from its configured identity and secrets; credentials are not retained in
the generated graph or website.

Serve the resulting `output/grapharch-project-site/site/` directory at any static
host. Internal links and bundled fonts/styles are relative, so it also works
under a GitHub Pages project path. The publication profile chooses the reusable
EKGF project layout. Ordinary Markdown headings define the hero, sections and
cards; there is no project-specific HTML template in this directory.

## Source and parity

The initial content was transcribed from the current public project pages on
2 November 2026, backed by this repository's `site/src/app/` pages (source revision
`1979af85577492a1e022f30fbe1b010c837d5b29`). Page text, links, lists and code
examples are retained. JSON and citation fences have explicit language metadata;
timeline status/date separators and the community contact link are normalized.
The source Next.js files remain in place until the pilot is reviewed.

The source-owned pages include home, why, concepts, adopt and roadmap. A
build-time version inventory discovers GitHub/Vercel publication versions and
produces the specification-version page and its routing manifest from the same
pinned documentation graph. Source-owned `ga:order` values keep the frozen release
and develop draft before previews. The page displays a readable UTC observation
time below the version-list heading. CI retains the native website KG alongside
the deployment for rendering without the original sources or API credentials.
The EKGF project theme supports a persistent light
or dark preference and uses the operating system's preference initially.

Frontmatter descriptions retain the current project's search descriptions. The
website target supplies the public canonical base, `https://ekgf.org/dprod/`;
GraphArch generates canonical/Open Graph metadata, a sitemap and robots file.
Preview deployments intentionally keep those production canonical URLs.

## Hosting and migration boundary

The generated artifact works as static files on Vercel or GitHub Pages; neither
requires a Next.js project. The project preview is retained as a CI artifact
beside the two PDF editions. The existing production Next.js deployment remains
active until the static preview is verified; no production integration has been
removed or switched by this workflow.

Remaining review work includes a complete preview browser/HTTP parity check,
version-inventory freshness triggers, referencing `/dprod/sitemap.xml` from the
main domain's root robots configuration, production routing cutover, and removing
the old application after successful cutover. The generated 404 page currently
uses a minimal document rather than the branded project shell.

### Static deployment preview

`publication/hosting.yml` assembles the generated project website with the
existing Python specification output and frozen 1.0 archive. It emits Vercel's
Build Output API directly, without Next.js or server functions. CI retains this
portable artifact and deploys a separate preview; it does not promote that
preview to production.

The `/dprod/` mount matches the existing EKGF website proxy. `/dprod/spec/` and
`/dprod/spec/develop/` serve the current specification; `/dprod/spec/main/` serves
the byte-identical frozen 1.0 release. The archive keeps its existing slashless
canonical URL. The contracts profile IRIs serve the published Turtle profile.
Other version URLs redirect to the deployment observed in the generated version
inventory, including versions omitted from the public listing.

The artifact's `static/` tree is also usable on a static host. For a GitHub Pages
project prefix, package with `--mount /` and publish that tree under the host's
configured project path. Remote version redirects and explicit RDF media types
remain hosting rules, so they require equivalent host routing configuration.

Production still uses the existing site until the static preview's URLs, assets,
version routing, and presentation have been verified. Removing that application
and changing the production deployment is a separate, reviewable cutover.
