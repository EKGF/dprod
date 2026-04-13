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

export async function middleware(req: NextRequest) {
  const parsed = parseSpecPath(req.nextUrl.pathname);
  if (!parsed) return NextResponse.next();
  const { slug, rest } = parsed;

  if (STATIC_SLUGS.has(slug)) return NextResponse.next();

  const versions = await getSpecVersions();
  const version = versions.find((v) => v.id === slug);
  if (!version || version.kind !== "vercel-branch") return NextResponse.next();

  // If the requested version matches the current deployment, serve locally
  // via same-origin rewrite — assets resolve normally. The destination must
  // include the basePath because req.nextUrl.pathname is wire-level.
  if (version.isCurrent) {
    const url = req.nextUrl.clone();
    url.pathname = `/dprod/spec${rest}`;
    return NextResponse.rewrite(url);
  }

  // For cross-branch targets we 307 to the actual deployment URL. The
  // origin already includes /dprod (see spec-versions.ts) so we only append
  // /spec<rest>.
  return NextResponse.redirect(`${version.origin}/spec${rest}`, 307);
}
