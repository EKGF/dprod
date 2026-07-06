import type { MetadataRoute } from "next";

/**
 * Sitemap for the DPROD zone.
 *
 * This app is served under ekgf.org/dprod/* (basePath: "/dprod") through
 * the ekgf-website multi-zone proxy, so every <loc> must be the public,
 * absolute ekgf.org/dprod URL — NOT this zone's own *.vercel.app origin.
 * With basePath set, Next serves this route at
 * https://ekgf.org/dprod/sitemap.xml, and the ekgf-website middleware
 * (matcher: /dprod/:path*) forwards it here.
 *
 * Canonical URL shapes match what each route actually resolves to:
 *  - App routes and the generated current spec keep a trailing slash
 *    (next.config.ts sets trailingSlash: true).
 *  - The static archived spec (public/spec/archive/1.0/index.html) is
 *    canonicalised WITHOUT a trailing slash — the slash form 308s away.
 */
const BASE_URL = "https://ekgf.org/dprod" as const;

// Last time the zone's content meaningfully changed. Bump on publish.
const LAST_MODIFIED = new Date("2026-06-17");

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    {
      url: `${BASE_URL}/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/spec/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/concepts/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/why/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/adopt/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/roadmap/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/spec-versions/`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      // Frozen archived release — canonical form has no trailing slash.
      url: `${BASE_URL}/spec/archive/1.0`,
      lastModified: LAST_MODIFIED,
      changeFrequency: "yearly",
      priority: 0.4,
    },
  ];
}
