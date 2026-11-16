import type { NextConfig } from "next";

/**
 * The primary zone proxies /dprod/:path* to this deployment, including
 * /dprod/_next/static/*. Keep browser assets on the requesting origin:
 * enterprise networks may block generated *.vercel.app deployment hosts.
 * Next.js applies basePath to asset URLs when assetPrefix is omitted, so
 * the same build works through ekgf.org and on its direct preview origin.
 */
const nextConfig: NextConfig = {
  basePath: "/dprod",
  // The spec HTML references sibling assets (images, downloads) with
  // relative URLs like `./assets/dprod.jpg` and `dprod.ttl`. Without a
  // trailing slash on the spec URL, the browser strips the last segment
  // when resolving those, so relative links land one directory too high
  // and 404. With `trailingSlash: true`, Next.js auto-redirects URLs
  // without a trailing slash to the slashed form, so relative URLs inside
  // the spec resolve against the intended directory. An earlier attempt
  // using an explicit `redirects()` entry for `/spec → /spec/` produced
  // a redirect loop because the default (`trailingSlash: false`) strips
  // the slash right back off.
  trailingSlash: true,
  async rewrites() {
    return [
      // /spec/ → current deployment's own generated spec
      // (basePath is automatically prepended, so this resolves to
      // /dprod/spec/ → /dprod/spec/index.html under the zone.)
      { source: "/spec/", destination: "/spec/index.html" },
      // The contracts profile is distinct from the ontology/term namespace.
      // Serve its RDF description at the profile identifier itself.
      {
        source: "/spec/contracts/profile/",
        destination: "/spec/dprod-contracts-prof.ttl",
      },
      // /spec/main/ → frozen OMG 1.0 archive
      { source: "/spec/main/", destination: "/spec/archive/1.0/index.html" },
      {
        source: "/spec/main/:path*",
        destination: "/spec/archive/1.0/:path*",
      },
      // /spec/archive/<version>/ directory index
      {
        source: "/spec/archive/:version/",
        destination: "/spec/archive/:version/index.html",
      },
    ];
  },
};

export default nextConfig;
