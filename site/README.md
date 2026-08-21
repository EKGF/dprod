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

## `GITHUB_TOKEN`

Required, and it must be **valid** — an expired or revoked token behaves
exactly like a missing one. Fine-grained tokens expire, so this will recur.

A fine-grained token needs only `Metadata: Read-only` on `EKGF/dprod`; no
write scopes. See `.env.example`.

When the branch lookup fails, two things happen and neither is silent:

- the reason is logged with `console.warn`, including GitHub's own message —
  `Bad credentials` for an expired or revoked token, a rate-limit message when
  running unauthenticated, `Resource not accessible` for a missing scope;
- the page renders a "Branch list unavailable" notice.

This matters because issue #249 was caused by the *absence* of both. The
picker advertised 22 branches, 11 of them deleted months earlier, while only 6
pull requests were open — and nothing anywhere reported that the filter had
stopped working. The token was configured the whole time; it simply was not
being accepted, which the old code could not distinguish from success.
