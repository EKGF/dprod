import { NextResponse, type NextRequest } from "next/server";
import { getSpecVersions } from "@/lib/spec-versions";

/**
 * Matches anything under /spec/<something>/..., so the middleware fires for
 * cross-branch spec routing. /spec and /spec/ (no suffix) fall through to
 * Next.js's normal static serving (current deployment's public/spec/).
 *
 * basePath /dprod is auto-applied by Next.js, so this matcher effectively
 * becomes /dprod/spec/:path+ in the wire URL.
 */
export const config = {
  matcher: "/spec/:path+",
};

// Slugs that are NOT Vercel branches and must fall through to other handlers:
//   - "main"     → handled by next.config.ts rewrite to /spec/archive/1.0
//   - "archive"  → static files under public/spec/archive
const STATIC_SLUGS = new Set(["main", "archive"]);

/**
 * Parse /spec/<slug>[/<rest>] — accepting an optional leading basePath so
 * the regex works whether or not Next.js has already stripped it.
 */
function parseSpecPath(pathname: string): { slug: string; rest: string } | null {
  const match = pathname.match(/^(?:\/dprod)?\/spec\/([^/]+)(\/.*)?$/);
  if (!match) return null;
  return { slug: match[1], rest: match[2] ?? "" };
}

function withDebug(
  res: NextResponse,
  tag: string,
  extras: Record<string, string | undefined> = {},
): NextResponse {
  res.headers.set("x-dprod-mw", tag);
  for (const [k, v] of Object.entries(extras)) {
    if (v !== undefined) res.headers.set(`x-dprod-mw-${k}`, v);
  }
  return res;
}

export async function middleware(req: NextRequest) {
  const parsed = parseSpecPath(req.nextUrl.pathname);
  if (!parsed) return withDebug(NextResponse.next(), "no-match");
  const { slug, rest } = parsed;

  if (STATIC_SLUGS.has(slug)) {
    return withDebug(NextResponse.next(), "static-slug", { slug });
  }

  const versions = await getSpecVersions();
  const version = versions.find((v) => v.id === slug);
  if (!version || version.kind !== "vercel-branch") {
    return withDebug(NextResponse.next(), "unknown-slug", {
      slug,
      versions: versions.map((v) => v.id).join(","),
    });
  }

  // If the requested version matches the current deployment, directly
  // rewrite to the static index.html inside public/spec/ under basePath.
  // We bypass the /spec -> /spec/index.html rewrite from next.config.ts
  // because chaining middleware rewrites through afterFiles rewrites is
  // unreliable in Next.js 16. We also construct the destination URL via
  // `new URL(path, req.url)` rather than `req.nextUrl.clone()` because
  // NextURL carries a basePath attribute and mutating its pathname leads
  // to double-prefix surprises.
  if (version.isCurrent) {
    const destPath = rest
      ? `/dprod/spec${rest}`
      : `/dprod/spec/index.html`;
    const destUrl = new URL(destPath, req.url);
    return withDebug(NextResponse.rewrite(destUrl), "self-rewrite", {
      slug,
      dest: destPath,
    });
  }

  // For cross-branch targets we 307 to the actual deployment URL. The
  // origin already includes /dprod (see spec-versions.ts) so we only append
  // /spec<rest>.
  return withDebug(
    NextResponse.redirect(`${version.origin}/spec${rest}`, 307),
    "cross-branch",
    { slug, origin: version.origin },
  );
}
