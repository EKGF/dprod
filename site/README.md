# DPROD site

The Next.js app served at `https://ekgf.org/dprod` (proxied verbatim from the
`ekgf-website` zone) and at `https://dprod.ekgf.vercel.app`.

## Spec version discovery

`src/lib/spec-versions.ts` builds the list behind `/spec-versions` and the
`/spec/<slug>` routing in `middleware.ts`. It combines two sources:

| Source | Question it answers | Env vars |
|---|---|---|
| Vercel deployments API | Which branches have a READY deployment? | `VERCEL_TOKEN`, `VERCEL_PROJECT_ID`, `VERCEL_ORG_ID` |
| GitHub branches API | Which of those branches still exist? | `GITHUB_TOKEN` |

Both are cached for 60 seconds via `next: { revalidate: 60 }`, so a new branch
appears without redeploying `develop`.

There are two entry points, and the difference matters:

- **`getSpecVersions()`** — everything routable. Permissive on purpose: the
  middleware resolves explicit `/spec/<slug>` URLs with it, and a URL someone
  already holds should keep working even when GitHub is unreachable.
- **`getListedSpecVersions()`** — what a reader is shown. Fails **closed**: if
  branch existence cannot be determined, it lists only the archive and
  `develop`.

`GITHUB_TOKEN` is required. Without it the branch lookup is unauthenticated,
GitHub's 60-requests-per-hour-per-IP limit is shared across Vercel's egress
addresses, and the lookup fails continuously. This is what caused the version
picker to advertise 22 branches — 11 of them deleted months earlier — while
only 6 pull requests were open (issue #249). The failure is now logged with
`console.warn`, visible in the Vercel runtime logs.

See `.env.example` for the token scopes needed.
