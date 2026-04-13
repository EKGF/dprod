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
  // via same-origin rewrite — assets resolve normally.
  if (version.isCurrent) {
    const url = req.nextUrl.clone();
    url.pathname = `/spec${rest}`;
    return NextResponse.rewrite(url);
  }

  // For cross-branch targets we 307 to the actual deployment URL instead of
  // proxy-rewriting. NextResponse.rewrite() to an external origin returns
  // the HTML body but does NOT rewrite the /_next/static/... asset paths
  // inside it — the browser then fetches assets from the current origin
  // (where the hashed filenames don't exist) and the page renders unstyled.
  // A redirect loses the /spec/<slug> URL in the address bar but everything
  // works. A future route handler could do HTML rewriting with <base> tag
  // injection for unified chrome, but not in phase 5.
  return NextResponse.redirect(`${version.origin}/spec${rest}`, 307);
}
