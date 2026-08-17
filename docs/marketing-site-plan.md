# DPROD Marketing Site — Implementation Plan

Tracks: [#174](https://github.com/EKGF/dprod/issues/174). Related: [#175](https://github.com/EKGF/dprod/issues/175) (Vercel previews), [#176](https://github.com/EKGF/dprod/issues/176) (parked generic publisher).

## Goal

Build a user-friendly, attractive explainer / marketing website for DPROD that sits alongside the normative spec in this repo, matches the `ekgf-website` design system, and becomes the primary destination for practitioners who want to understand what DPROD is, why it exists, and how to adopt it.

## Non-goals (for this branch)

- Replacing the Python + ReSpec spec generator. It keeps working; its output is embedded as-is.
- Vercel project / custom domain setup — covered by #175, done after this branch lands.
- Sharing a component library between `dprod` and `ekgf-website`. We copy, not extract, for now.
- Touching the `main` branch in any way (see constraint below).

## Hard constraint: `main` is frozen

The `main` branch contains the version of DPROD that has been formally approved by OMG as a standard. It **must not** be rebuilt, re-run through CI, re-processed by the spec generator, or auto-deployed by Vercel. Any re-run carries the risk of emitting output that differs from the approved bytes (fonts, tooling versions, remote vocab fetches, generator changes), which would be a governance problem.

Consequences for this plan:

- Vercel configuration for the `dprod` repo must **exclude** `main` from auto-deployment. In `vercel.json`:
  ```json
  {
    "git": { "deploymentEnabled": { "main": false, "develop": true } }
  }
  ```
  Every other branch gets preview deployments; `main` does not.
- The frozen 1.0 is served from the archived snapshot at <https://ekgf.org/dprod/spec/archive/1.0/> (also `/spec/main`). The original GitHub Pages site (`ekgf.github.io/dprod`) is retired and returns 404.
- `/spec/main` in the new marketing site is served from a one-time static snapshot committed into `develop` under `site/public/spec/archive/1.0/`, downloaded verbatim from GitHub Pages and never regenerated. No rewrite, no external runtime dependency.
- The 1.0 snapshot is downloaded from GitHub Pages once and committed at `site/public/spec/archive/1.0/` as part of phase 5. This makes the site self-contained — if Pages is ever retired, the archived content is already in the repo and nothing breaks.
- The working-group-facing `bash build.sh` is only ever run against branches that descend from `develop`. CI must not invoke it on `main`.

## Content ownership: move, don't fork

All DPROD-specific content currently lives in `ekgf-website/src/app/dprod/page.tsx` (~540 lines — elevator pitch, origins & standardization, key benefits, articles & talks, core concepts, use cases, CTA to spec / OMG / repo). That's the wrong home: dprod content should live in the dprod repo so the working group can iterate on it without touching ekgf-website.

**The move is part of this effort, not a follow-up.** The plan has two deliverables that ship together:

1. **PR #1** (this branch, `dprod` repo) — new `site/` Next.js app that becomes the canonical DPROD website, with all existing content moved in and extended.
2. **PR #2** (`ekgf-website` repo) — `src/app/dprod/page.tsx` reduced to a short teaser card that links out to the new standalone DPROD site, or — if we use `ekgf.org/dprod` as the domain via Next.js rewrites — the file is removed entirely.

PR #2 merges **after** PR #1 and after the new site has a reachable URL, so ekgf.org never has a dead DPROD link. Both PRs reference #174.

## Architecture

```
dprod/                               (this repo)
├─ spec-generator/      Python generator (unchanged)
├─ ontology/            OWL + SHACL sources (unchanged)
├─ examples/            worked examples (unchanged)
├─ respec/              ReSpec template (unchanged for now)
├─ build.sh             Python build entry point (unchanged)
├─ dist/                intermediate Python output → copied into public/spec/
└─ site/                NEW — Next.js marketing app
   ├─ src/
   │  ├─ app/           App Router pages
   │  ├─ components/    UI components (ported from ekgf-website)
   │  └─ lib/
   ├─ public/
   │  └─ spec/          populated at build time from dprod/dist/
   ├─ next.config.ts
   ├─ package.json
   └─ tsconfig.json
```

Keeping the Next.js app under `site/` isolates it from the Python generator, lets `pnpm` operate in a self-contained directory, and makes future extraction trivial if we ever want to move it.

## Stack (match `ekgf-website` exactly)

- Next.js 16 (App Router, Turbopack)
- React 19
- TypeScript, strict
- Tailwind CSS 4
- shadcn-style primitives via `@radix-ui/*`
- `lucide-react` icons
- `next-themes` for dark mode
- `pnpm@10` as package manager

Rationale: matching the stack means components, tokens, and content port cleanly, and the design system stays coherent with ekgf.org. This is a hard requirement.

## Information architecture

Flat and shallow. No deep nav. Pages:

1. **`/`** — Landing. Hero, what is DPROD in one paragraph, 3–4 benefit cards, link to spec, link to articles, link to GitHub. Port the existing ekgf.org hero + benefit cards.
2. **`/why`** — Vision & motivation. Why data products, why an ontology, relationship to data mesh, the "semantic foundation prevents data mess" argument. Expands what's currently squeezed into the ekgf.org page.
3. **`/concepts`** — Core concepts (Data Product, Ports, Distributions & Datasets). Port from ekgf.org. Each concept links to its class section in `/spec/`.
4. **`/adopt`** — Getting started. Worked examples (link into `examples/`), how to cite DPROD, who uses it, tooling hints.
5. **`/roadmap`** — Ballot process, upcoming work, how the standard evolves, how to contribute. New content, not on ekgf.org today.
6. **`/spec/`** — The generated normative spec, served as static files (see "Spec integration" below). Not a Next.js route — Vercel serves `public/spec/index.html` directly.

Header nav: Home · Why · Concepts · Adopt · Roadmap · Spec → · GitHub →

Footer: EKGF attribution, OMG links, copyright (EDM Council, Inc.), license.

## Spec integration

The Python generator already produces `dist/index.html` plus assets and RDF serializations. We do not change how it works. Instead:

1. `build.sh` continues to write to `dist/` at the repo root.
2. A small step copies `dist/` into `site/public/spec/` before `next build` runs (either via `site/package.json`'s `prebuild` script or a one-line shell step in the Vercel build command).
3. Next.js serves `site/public/spec/index.html` at `/spec/` verbatim for the *current deployment's own* build (see "Versioned spec routes" below for cross-branch access).
4. Links *from* the marketing pages *into* the spec use `/spec/#<anchor>` — the anchors (`#dataproductshape`, etc.) already exist thanks to DPROD-21.
5. Links *from* the spec *out* to the marketing site are deferred — the ReSpec template stays untouched on this branch.

Local dev: `cd site && pnpm dev` assumes `../dist` is already populated. A `pnpm sync-spec` helper script copies `../dist` → `public/spec/` on demand. CI always runs `bash build.sh` first.

## Versioned spec routes

Reviewers and readers need to jump between spec versions: the frozen OMG 1.0, the current `develop`, and in-flight ballot branches. The URL shape is `/spec/<version>`, e.g. `/spec/develop`, `/spec/main`, `/spec/ballot/4`.

### Semantics

- **`/spec/`** — always serves the current deployment's *own* generated spec. On the production (develop) deployment this is develop's latest; on a PR preview it's that PR's spec. Reviewers clicking "Spec" in the nav of a PR preview get the right thing without thinking about it. This is what the `sync-spec` step above populates.
- **`/spec/<version>`** — a cross-branch reference implemented as a Next.js `rewrite` (in `site/next.config.ts`) to the corresponding Vercel preview deployment's `/spec/`. Vercel preview URLs are stable per branch (`dprod-git-<branch>-ekgf.vercel.app`), so rewrites can target them by hostname. Branch slashes are normalised: `ballot/4` → `ballot-4` in the host, but the URL path `/spec/ballot/4` is preserved for readability.
- **`/spec/main`** — served from a one-time static snapshot committed into the `develop` branch at `site/public/spec/archive/1.0/`. The content was downloaded verbatim from the now-retired GitHub Pages site (wget/curl of the full site) and committed once; its retired-URL references were later rewritten to their successors so the archive serves no dead links. No rewrite, no proxy, no runtime external dependency, no separate branch needed. The Python generator is never invoked to produce this content.

Crucially, `/spec/` and `/spec/main` are both plain static routes — no rewrites involved. Only `/spec/<other-branch>` routes invoke Vercel rewrites to other deployments.

### Version list as data

A single source of truth in `site/src/lib/spec-versions.ts`:

```ts
export type SpecVersion = {
  id: string;                    // URL slug: "develop", "main", "ballot-4"
  label: string;                 // UI label: "Develop (latest)", "1.0 (OMG approved)"
  description?: string;          // short explainer for the picker
  isDefault?: boolean;           // one version is marked as the canonical default
  destination:
    | { kind: "vercel-branch"; branch: string }  // rewrite to another Vercel deployment
    | { kind: "archive"; path: string }           // static snapshot under public/spec/archive/
    | { kind: "self" };                           // no rewrite; serve this deployment's own /spec/
};

export const SPEC_VERSIONS: SpecVersion[] = [
  {
    id: "develop",
    label: "Develop (latest)",
    description: "The current working draft on the develop branch.",
    isDefault: true,
    destination: { kind: "vercel-branch", branch: "develop" },
  },
  {
    id: "main",
    label: "1.0 (OMG approved)",
    description: "The frozen version approved by OMG as the official standard. Never rebuilt.",
    destination: { kind: "archive", path: "/spec/archive/1.0/" },
  },
  // ballots added per live ballot, e.g.:
  // { id: "ballot-4", label: "Ballot 4 (in review)", destination: { kind: "vercel-branch", branch: "ballot/4" } },
];
```

`next.config.ts` generates `rewrites()` from `SPEC_VERSIONS`, so adding a new ballot version is a one-line PR.

### UI: version picker

A `<VersionPicker>` component renders in the spec page chrome (a thin sticky header above the embedded `/spec/index.html`, not inside the ReSpec document itself since that HTML is served as-is). The picker:

- Reads `SPEC_VERSIONS`.
- Highlights the version matching the current route (or `isDefault` on the bare `/spec/` route).
- Renders each version as a link to `/spec/<id>`.
- On PR / preview deployments, shows a banner: "You are viewing an in-flight preview: `<VERCEL_GIT_COMMIT_REF>`. [View canonical develop →]". The banner uses `process.env.VERCEL_GIT_COMMIT_REF` resolved at build time.

Since the picker sits above the spec iframe/embed, it needs a layout that doesn't conflict with ReSpec's own navigation. Simplest approach: a Next.js layout route at `site/src/app/spec/layout.tsx` that wraps the picker chrome; the actual spec HTML is served from `public/spec/` and referenced via an `<iframe>` or — better — a dedicated Next.js route that reads the HTML and injects it. To be decided in phase 5.

### Linking from marketing pages

Marketing content links to **specific concepts**, not specific versions. The `/concepts` page links use `/spec/#dataproductshape`, which resolves against whatever `/spec/` currently serves on the deployment the reader is on. If a reader on the develop-deployment wants to see how a concept looked in 1.0, they use the version picker from the spec view itself. This avoids scattering version-aware links throughout the marketing copy.

## Design system

Don't invent. Port from `ekgf-website`:

- `tailwind.config` + `globals.css` (Tailwind v4 CSS-first tokens)
- `src/components/ui/*` (button, card, navigation-menu, theme-toggle, etc.)
- Color tokens in use on the existing page: `#4051b5` (indigo primary), `#ff6f00` (orange accent). Keep them.
- Fonts: inherit whatever ekgf-website uses (check at port time).

Do not copy wholesale layout chrome (header/footer) from ekgf.org — they belong to that site. Build minimal DPROD-specific chrome that *looks* consistent.

## Build & dev workflow

| Command | What it does |
|---|---|
| `bash build.sh` | Generate the spec into `dist/` (unchanged) |
| `cd site && pnpm install` | Install Next.js deps |
| `cd site && pnpm sync-spec` | Copy `../dist/` → `public/spec/` |
| `cd site && pnpm dev` | Run Next.js dev server on `localhost:3000` |
| `cd site && pnpm build` | Production build (runs `sync-spec` as `prebuild`) |
| `cd site && pnpm start` | Serve production build |

Root `Makefile` gains a `site` target that runs the full chain end-to-end for sanity checks.

## Phase breakdown

Each phase should land as its own commit, and the branch is mergeable-in-principle after each one.

### Phase 1 — Scaffold
- Create `site/` with Next.js 16 app template matching `ekgf-website`.
- Copy `package.json` deps, `tsconfig.json`, `next.config.ts`, `postcss.config.mjs`, `eslint.config.mjs`, `components.json` with adjustments.
- Add `.gitignore` entries for `site/node_modules`, `site/.next`, `site/public/spec`.
- Verify `pnpm install && pnpm dev` renders a placeholder home page.

### Phase 2 — Design system port
- Copy `src/components/ui/*` primitives we need (button, card, navigation-menu).
- Copy `globals.css` + Tailwind config. Verify tokens resolve.
- Build minimal `Header` + `Footer` components for DPROD chrome.
- Add theme provider (`next-themes`) + theme toggle.

### Phase 3 — Landing page (`/`)
- Move the hero + benefit cards + articles section from `ekgf-website/src/app/dprod/page.tsx` (lines ~25–350) into the new `site/`.
- Verify visual parity with the existing ekgf.org DPROD page — the new site should be a strict superset of what ekgf.org shows today.

### Phase 4 — Supporting pages
- `/why` — move & expand the "What is DPROD" + origins content from the ekgf-website page.
- `/concepts` — move the Core Concepts section, link each into `/spec/#...`.
- `/adopt` — move the CTA card + reference to worked examples; add a short "how to cite" block.
- `/roadmap` — net-new content. Start with a placeholder timeline: current ballot, recently closed ballots, "how ballots work" explainer.

By the end of phase 4, the dprod repo holds **every piece of content** currently shown on `ekgf.org/dprod`, plus the new roadmap / vision material.

### Phase 5 — Spec integration
- Add `pnpm sync-spec` script (simple Node or shell).
- Wire `prebuild` to run it.
- Verify `/spec/` serves `dist/index.html` and that `/spec/#dataproductshape` works.
- Make sure internal links from `/concepts` resolve into the spec.
- Add `site/src/lib/spec-versions.ts` with the initial list (develop = self-or-vercel-branch, main = github-pages).
- Generate `rewrites()` in `next.config.ts` from `SPEC_VERSIONS`.
- Build the `<VersionPicker>` chrome at `site/src/app/spec/layout.tsx`, including the preview banner driven by `VERCEL_GIT_COMMIT_REF`.
- Download the then-current GitHub Pages output with `wget -m -p -k` (or `curl` equivalent) and commit it verbatim into `site/public/spec/archive/1.0/`. This is a one-time manual step; it is not part of the build. (Done; the source site has since been retired.)
- Verify `/spec/main` serves the archived 1.0 content (pure static route — works immediately, no Vercel dependency).
- Verify `/spec/develop` rewrite works. This can only be end-to-end tested once #175 (Vercel project) is live — until then, verify locally by temporarily hard-coding the rewrite destination.

### Phase 6 — Polish
- Metadata (`metadata` exports, Open Graph images, favicon).
- `robots.ts`, `sitemap.ts`.
- Accessibility pass (keyboard nav, alt text, color contrast).
- README updates for how to run the site locally.

### Phase 7 — `ekgf-website` companion PR
Opened against `~/Work/ekgf-website` (separate repo, separate PR, same issue #174).

- If the new site is reachable at `dprod.ekgf.org` (preferred): replace `src/app/dprod/page.tsx` with a short teaser card (title, one-paragraph intro, prominent outbound link). Keep the route so inbound links don't 404.
- If the new site is reached via `ekgf.org/dprod` Next.js rewrite: delete `src/app/dprod/page.tsx` and its imports entirely; add the rewrite rule in `next.config.ts`.
- Either way: remove DPROD-specific links from the ekgf-website nav that duplicate the new standalone site.
- Merges **after** the dprod-repo PR is live and the new site is reachable. Never before.

Phase 8+ (deferred to separate issues): Vercel project creation (#175), replacing ReSpec (#176).

## Open questions

- **Spec embedding technique**: should `/spec/` use an `<iframe>` into `public/spec/index.html`, or should a Next.js server route read the HTML and render it inside the layout? Iframe is trivial but loses deep-link sharing and makes the VersionPicker chrome awkward. Reading and re-emitting the HTML is cleaner but requires a small HTML-rewriter pass so assets resolve. Decide in phase 5; recommend the server-route approach.
- **Domain**: `dprod.ekgf.org` vs `ekgf.org/dprod` (rewrite) vs both? The user example uses `ekgf.org/dprod/spec/main`, which points at a path-based integration via an `ekgf-website` rewrite. The subdomain is still cleaner for per-branch Vercel previews. Both are compatible with the version-routing design — rewrites work the same either way. Decide before #175.
- **`main` vs `develop` as production**: spec site should track `develop`; the frozen OMG 1.0 needs a pinned alias (e.g. `1-0.dprod.ekgf.org` or simply keep the existing GitHub Pages URL as the canonical historical artifact). Decide before #175.
- **Where does `ekgf.org/dprod` go after launch?** Decided: the page is either removed (if we use an ekgf.org rewrite) or reduced to a teaser card linking to the standalone site. Handled in phase 7 as a companion PR against `ekgf-website`. Still open: which of the two (rewrite vs teaser) we actually pick — that depends on the domain decision above.
- **Dark mode**: ekgf-website has `next-themes` — mirror it, or ship light-only for v1? Recommend mirror, it's ~free.
- **Content ownership**: do the sections on `/why` and `/roadmap` need sign-off from Tony / Pete / Marcel before the branch merges? Probably yes for public launch, not for an internal preview.
