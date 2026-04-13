import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // /spec → current deployment's own generated spec
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
