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

A branch deleted from `origin` drops off the listing, **including `ballot/*`**.
Its Vercel deployment survives and `/spec/<slug>` still resolves, so any URL
already published keeps working — it is simply no longer advertised. This is
deliberate (issue #249): the listing answers "which versions exist now?", and
a deleted branch does not. If a ballot needs to stay listed after its branch is
gone, keep the branch on `origin` rather than special-casing it here.

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

A fine-grained token needs **`Contents: Read-only`** on `EKGF/dprod` — that is
the permission `GET /repos/{owner}/{repo}/branches`
[requires](https://docs.github.com/en/rest/branches/branches). GitHub adds the
mandatory `Metadata: Read-only` automatically. No write permissions, and no
Pull requests permission: the lookup does not use that endpoint.

The repository is public, so the endpoint would also answer an unauthenticated
request — but that path carries GitHub's 60-requests-per-hour-per-IP limit,
shared across Vercel's egress, which is exactly the failure mode being avoided.
Granting `Contents: Read-only` is what makes the request authenticated, at
5,000 requests per hour.

See `.env.example`.

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
