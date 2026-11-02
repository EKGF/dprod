# DPROD project-site pilot

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

The pilot includes the home, why, concepts, adopt and roadmap routes. It does
**not** replace the live specification-version service or cross-branch routing.
Those currently query GitHub/Vercel on requests; the generated site links to that
existing service, rather than publishing a stale list of branch deployments.
The normative and development specification sites, downloads and PDF edition
pipelines are unchanged.

## Hosting and migration boundary

The generated artifact works as static files on Vercel or GitHub Pages; neither
requires a Next.js project. Production cutover still requires preserving the
`/dprod/` zone's specification rewrites, the live version service, SEO redirects,
and the existing archived specification URLs. The current pilot is light-theme
only; the existing project site's dark-mode toggle is not yet reproduced. A build-time version inventory
with an explicit freshness policy can eventually replace that service.

The project preview is retained as a CI artifact beside the two PDF editions.
This pilot does not remove or switch the existing production Next.js deployment.
