import { NextResponse, type NextRequest } from "next/server";
import { getSpecVersions } from "@/lib/spec-versions";

/**
 * Matches anything under /spec/<something>/..., so the middleware fires for
 * cross-branch spec routing. /spec and /spec/ (no suffix) fall through to
 * Next.js's normal static serving (current deployment's public/spec/).
 */
export const config = {
  matcher: "/spec/:path+",
};

// Slugs that are NOT Vercel branches and must fall through to other handlers:
//   - "main"     → handled by next.config.ts rewrite to /spec/archive/1.0
//   - "archive"  → static files under public/spec/archive
const STATIC_SLUGS = new Set(["main", "archive"]);

export async function middleware(req: NextRequest) {
  const match = req.nextUrl.pathname.match(/^\/spec\/([^/]+)(\/.*)?$/);
  if (!match) return NextResponse.next();
  const [, slug, rest = ""] = match;

  if (STATIC_SLUGS.has(slug)) return NextResponse.next();

  const versions = await getSpecVersions();
  const version = versions.find((v) => v.id === slug);
  if (!version || version.kind !== "vercel-branch") return NextResponse.next();

  // If the requested version matches the current deployment, serve locally
  // rather than looping back through the API.
  if (version.isCurrent) {
    const url = req.nextUrl.clone();
    url.pathname = `/spec${rest}`;
    return NextResponse.rewrite(url);
  }

  // Otherwise proxy to the branch's own Vercel deployment.
  return NextResponse.rewrite(`${version.origin}/spec${rest}`);
}
