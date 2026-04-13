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
  kind: SpecVersionKind;
};

const ARCHIVE_1_0: SpecVersion = {
  id: "main",
  label: "1.0 (OMG approved)",
  description: "The frozen version approved by OMG as the official standard. Never rebuilt.",
  branch: "main",
  origin: "",
  isCurrent: false,
  isProduction: false,
  kind: "archive",
};

/** Branches that we never want to advertise as spec versions. */
const EXCLUDED_BRANCHES = new Set<string>(["main"]);

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

/**
 * Returns the list of spec versions, in display order:
 *   1. The frozen 1.0 archive (always first, always present).
 *   2. develop (if deployed).
 *   3. Every other branch with a READY deployment, latest first.
 *
 * Never throws — on any failure, returns at least the archive entry so
 * /spec/main keeps working.
 */
export async function getSpecVersions(): Promise<SpecVersion[]> {
  const currentBranch = process.env.VERCEL_GIT_COMMIT_REF;
  const versions: SpecVersion[] = [ARCHIVE_1_0];

  const deployments = await fetchDeployments();

  const seen = new Set<string>();
  for (const dep of deployments) {
    const branch = dep.meta?.githubCommitRef;
    if (!branch || EXCLUDED_BRANCHES.has(branch) || seen.has(branch)) continue;
    seen.add(branch);

    const slug = branchToSlug(branch);
    versions.push({
      id: slug,
      label: labelForBranch(branch),
      description: descriptionForBranch(branch),
      branch,
      origin: `https://dprod-git-${slug}-ekgf.vercel.app`,
      isCurrent: branch === currentBranch,
      isProduction: branch === "develop",
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
