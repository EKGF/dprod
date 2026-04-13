import type { NextConfig } from "next";

/**
 * Multi-zone configuration.
 *
 * The dprod site is served as a Next.js zone under the /dprod path prefix.
 * The primary zone (ekgf-website) rewrites /dprod/:path* to whichever
 * deployment of this project it's targeting. When that happens the HTML
 * has absolute asset URLs back to this deployment's origin so CSS and JS
 * resolve across the zone boundary.
 *
 * basePath:   all routes, rewrites, middleware matcher paths are served
 *             under /dprod.
 * assetPrefix: every /_next/static/... URL in the generated HTML is
 *             absolute to this deployment's own origin. We read
 *             VERCEL_URL at build time (unique per deployment, always
 *             reachable) and prepend https://. On local dev VERCEL_URL
 *             is undefined and assetPrefix falls back to relative paths
 *             so localhost:3000 still works.
 */
const vercelUrl = process.env.VERCEL_URL;
// IMPORTANT: include the /dprod basePath in the assetPrefix. With basePath
// set, Next.js serves _next/* assets at /dprod/_next/*, but assetPrefix is
// written to the HTML as-is without the basePath being re-appended, so we
// have to include it ourselves or every asset 404s across the zone
// boundary.
const assetPrefix = vercelUrl ? `https://${vercelUrl}/dprod` : undefined;

const nextConfig: NextConfig = {
  basePath: "/dprod",
  assetPrefix,
  async rewrites() {
    return [
      // /spec → current deployment's own generated spec
      // (basePath is automatically prepended, so this resolves to
      // /dprod/spec → /dprod/spec/index.html under the zone.)
      { source: "/spec", destination: "/spec/index.html" },
      // /spec/main → frozen OMG 1.0 archive
      { source: "/spec/main", destination: "/spec/archive/1.0/index.html" },
      {
        source: "/spec/main/:path*",
        destination: "/spec/archive/1.0/:path*",
      },
      // /spec/archive/<version> directory index
      {
        source: "/spec/archive/:version",
        destination: "/spec/archive/:version/index.html",
      },
    ];
  },
};

export default nextConfig;
