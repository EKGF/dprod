/**
 * Discover the list of DPROD spec versions available across all Vercel
 * deployments of this project, plus the frozen OMG 1.0 archive.
 *
 * Used by:
 *   - middleware.ts (to route /spec/<slug>/... requests)
 *   - any Server Component that wants to render a version picker
 *
 * Freshness: we hit the Vercel API with `fetch` and let Next.js ISR cache
 * the response for 60s. This means:
 *   - Within a 60s window, picker + middleware share one cached result.
 *   - When a new branch gets deployed, the current production deployment
 *     picks it up on the next request after its window expires — no
 *     develop-branch redeploy required.
 *   - Stale data for at most ~60s, acceptable for this use case.
 */

export type SpecVersionKind = "archive" | "vercel-branch";

export type SpecVersion = {
  /** URL slug used in /spec/<id> (branch slashes replaced with dashes) */
  id: string;
  /** Human-readable label for the picker UI */
  label: string;
  /** Short description of what this version represents */
  description: string;
  /** Actual git branch name (may contain slashes) */
  branch: string;
  /** Origin of the deployment serving this version, or "" for local archive */
  origin: string;
  /** True if this version matches the current deployment's branch */
  isCurrent: boolean;
  /** True if this version is the production branch (develop) */
  isProduction: boolean;
  /**
   * Whether the branch still exists upstream. `null` means the lookup was
   * unavailable, so existence is unknown — never treat that as "yes".
   */
  existsUpstream: boolean | null;
  kind: SpecVersionKind;
};

const ARCHIVE_1_0: SpecVersion = {
  id: "main",
  label: "DPROD 1.0 (Beta)",
  description: "The frozen version approved by OMG as the official standard. Never rebuilt.",
  branch: "main",
  origin: "",
  isCurrent: false,
  isProduction: false,
  existsUpstream: true,
  kind: "archive",
};

/** Branches that we never want to advertise as spec versions. */
const EXCLUDED_BRANCHES = new Set<string>(["main"]);

/**
 * Branch prefixes that are never spec versions. A dependency bump produces a
 * perfectly valid preview deployment, but it is not a version of the
 * specification and only adds noise to the picker.
 */
const EXCLUDED_BRANCH_PREFIXES = ["dependabot/"];

function isAdvertisableBranch(branch: string): boolean {
  if (EXCLUDED_BRANCHES.has(branch)) return false;
  return !EXCLUDED_BRANCH_PREFIXES.some((prefix) => branch.startsWith(prefix));
}

function branchToSlug(branch: string): string {
  return branch.replace(/\//g, "-");
}

function labelForBranch(branch: string): string {
  if (branch === "develop") return "Develop (latest)";
  return branch;
}

function descriptionForBranch(branch: string): string {
  if (branch === "develop") return "The current working draft on the develop branch.";
  if (branch.startsWith("ballot/")) return `Ballot ${branch.slice(7)} — in review.`;
  return `Preview build of the ${branch} branch.`;
}

type VercelDeployment = {
  meta?: { githubCommitRef?: string };
  state?: string;
  url?: string;
};

async function fetchDeployments(): Promise<VercelDeployment[]> {
  const token = process.env.VERCEL_TOKEN;
  const projectId = process.env.VERCEL_PROJECT_ID;
  const teamId = process.env.VERCEL_ORG_ID;

  if (!token || !projectId || !teamId) {
    return [];
  }

  const url = new URL("https://api.vercel.com/v6/deployments");
  url.searchParams.set("projectId", projectId);
  url.searchParams.set("teamId", teamId);
  url.searchParams.set("state", "READY");
  url.searchParams.set("limit", "100");

  try {
    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${token}` },
      // Cache the Vercel API response for 60s — shared across middleware +
      // Server Components for a given revalidation window.
      next: { revalidate: 60 },
    });
    if (!res.ok) return [];
    const data = (await res.json()) as { deployments?: VercelDeployment[] };
    return data.deployments ?? [];
  } catch {
    return [];
  }
}

type GitHubBranch = {
  name?: string;
};

/**
 * Every branch that currently exists in the repository, or `null` when the
 * lookup was unavailable.
 *
 * Existence — not open-PR status — is the right question. A branch whose PR
 * has merged is normally deleted, and its Vercel preview, while still
 * reachable by URL, is no longer a version of anything. Conversely a branch
 * can legitimately exist with no open PR (merged but kept, or pushed before
 * the PR is raised), and an open-PR filter hid those too.
 *
 * Returns `null` rather than an empty set on failure, so callers can tell
 * "no branches" apart from "could not ask" — very different things.
 *
 * Every failure path logs the status and GitHub's own message. The bug this
 * replaced (issue #249) was undiagnosable from outside precisely because it
 * failed silently: a present-but-rejected token looks exactly like a missing
 * one when nothing is logged.
 */
async function fetchExistingBranches(): Promise<Set<string> | null> {
  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    // Unauthenticated GitHub allows 60 requests/hour per IP, shared across
    // every function on that egress address, so this is not a
    // degraded-but-workable path — it fails continuously.
    console.warn(
      "[spec-versions] GITHUB_TOKEN is not set; cannot determine which " +
        "branches still exist. Showing the archive and develop only.",
    );
    return null;
  }

  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    Authorization: `Bearer ${token}`,
    // GitHub rejects requests without a User-Agent with 403. Runtimes differ
    // in whether they supply a default, so set one explicitly rather than
    // depending on the platform.
    "User-Agent": "ekgf-dprod-site",
  };

  const branches = new Set<string>();
  // The repository has far fewer than 100 branches today, but paginate
  // anyway: silently truncating would hide live branches.
  for (let page = 1; page <= 10; page++) {
    let res: Response;
    try {
      res = await fetch(
        `https://api.github.com/repos/EKGF/dprod/branches?per_page=100&page=${page}`,
        { headers, next: { revalidate: 60 } },
      );
    } catch (error) {
      console.warn("[spec-versions] GitHub branch lookup threw:", error);
      return null;
    }
    if (!res.ok) {
      // GitHub's body distinguishes the cases that matter: "Bad credentials"
      // (401, token expired or revoked), "API rate limit exceeded" (403),
      // and resource-not-accessible (403, token lacks Metadata: Read-only).
      const detail = await res.text().catch(() => "");
      console.warn(
        `[spec-versions] GitHub branch lookup failed: ${res.status} ` +
          `${res.statusText}. ${detail.slice(0, 300)}`,
      );
      return null;
    }
    const pageBranches = (await res.json()) as GitHubBranch[];
    for (const branch of pageBranches) {
      if (branch.name) branches.add(branch.name);
    }
    if (pageBranches.length < 100) break;
  }
  return branches;
}

/**
 * Every spec version this deployment can *route* to: the frozen archive plus
 * each branch with a READY Vercel deployment.
 *
 * Intentionally permissive. The middleware uses this to resolve an explicit
 * /spec/<slug> URL, and a URL someone already holds should keep working even
 * while the GitHub lookup is unavailable. Use `getListedSpecVersions()` for
 * anything user-facing.
 *
 * Never throws — on any failure it still returns the archive entry, so
 * /spec/main keeps working.
 */
export async function getSpecVersions(): Promise<SpecVersion[]> {
  const currentBranch = process.env.VERCEL_GIT_COMMIT_REF;
  const versions: SpecVersion[] = [ARCHIVE_1_0];

  const [deployments, existingBranches] = await Promise.all([
    fetchDeployments(),
    fetchExistingBranches(),
  ]);

  const seen = new Set<string>();
  for (const dep of deployments) {
    const branch = dep.meta?.githubCommitRef;
    if (!branch || !isAdvertisableBranch(branch) || seen.has(branch)) continue;
    seen.add(branch);

    const slug = branchToSlug(branch);
    // NOTE: the origin uses the per-branch preview domain managed by
    // .github/workflows/vercel-branch-domains.yml (which registers
    // <slug>.dprod-preview.ekgf.org against each PR branch), and
    // intentionally includes the /dprod basePath so the middleware
    // redirect lands on the zone root, not the deployment root (which is
    // a 404 under multi-zone).
    versions.push({
      id: slug,
      label: labelForBranch(branch),
      description: descriptionForBranch(branch),
      branch,
      origin: `https://${slug}.dprod-preview.ekgf.org/dprod`,
      isCurrent: branch === currentBranch,
      isProduction: branch === "develop",
      existsUpstream: existingBranches ? existingBranches.has(branch) : null,
      kind: "vercel-branch",
    });
  }

  // Put develop right after the archive for UI consistency
  versions.sort((a, b) => {
    if (a.kind === "archive") return -1;
    if (b.kind === "archive") return 1;
    if (a.isProduction) return -1;
    if (b.isProduction) return 1;
    return a.branch.localeCompare(b.branch);
  });

  return versions;
}

/**
 * What a reader is shown, plus whether the list could be filtered at all.
 */
export type ListedSpecVersions = {
  versions: SpecVersion[];
  /**
   * False when branch existence could not be determined, so the list is the
   * fail-closed minimum rather than the real set. Surfaced in the UI: a
   * silently short list is as misleading as a silently long one.
   */
  complete: boolean;
};

/**
 * The spec versions to show a reader: the archive, develop, and branches that
 * still exist upstream.
 *
 * Fails *closed*. When branch existence is unknown the picker shows only the
 * archive and develop, because the alternative — what shipped before issue
 * #249 — was every branch ever deployed, including many deleted months
 * earlier. A short list is a smaller lie than a wrong one, and
 * `getSpecVersions()` still routes any preview URL that has been handed out.
 */
export async function getListedSpecVersions(): Promise<ListedSpecVersions> {
  const versions = await getSpecVersions();
  const complete = !versions.some(
    (version) => version.kind === "vercel-branch" && version.existsUpstream === null,
  );
  return {
    complete,
    versions: versions.filter(
      (version) =>
        version.kind === "archive" ||
        version.isProduction ||
        version.existsUpstream === true,
    ),
  };
}
