import assert from "node:assert/strict";
import { test } from "node:test";
import { registerHooks } from "node:module";
import { getSpecVersions } from "../src/lib/spec-versions.ts";

// Resolve the same aliases Next.js supplies when loading the middleware.
registerHooks({
  resolve(specifier, context, nextResolve) {
    if (specifier === "@/lib/spec-versions") {
      return nextResolve(new URL("../src/lib/spec-versions.ts", import.meta.url).href, context);
    }
    return nextResolve(specifier === "next/server" ? "next/server.js" : specifier, context);
  },
});
const { middleware } = await import("../middleware.ts");
const { NextRequest } = await import("next/server.js");

test("production serves Develop locally even when deployed from a feature branch", async (t) => {
  const originalEnv = { ...process.env };
  t.after(() => { process.env = originalEnv; });
  process.env.VERCEL_ENV = "production";
  process.env.VERCEL_GIT_COMMIT_REF = "issue/255-spec-header-urls";
  process.env.VERCEL_TOKEN = "test";
  process.env.VERCEL_PROJECT_ID = "test";
  process.env.VERCEL_ORG_ID = "test";
  process.env.GITHUB_TOKEN = "test";
  t.mock.method(globalThis, "fetch", async (url) => new Response(JSON.stringify(
    String(url).includes("api.vercel.com")
      ? { deployments: [{ meta: { githubCommitRef: "develop" } }] }
      : [],
  )));

  const develop = (await getSpecVersions()).find((v) => v.id === "develop");
  assert.ok(develop);
  assert.equal(develop.isCurrent, true);
  assert.equal(develop.origin, "https://ekgf.org/dprod");

  const response = await middleware(new NextRequest("https://ekgf.org/dprod/spec/develop/"));
  assert.equal(response.headers.get("location"), null);
  assert.equal(response.headers.get("x-dprod-mw"), "self-rewrite");
  assert.equal(response.headers.get("x-middleware-rewrite"), "https://ekgf.org/dprod/spec/");

  process.env.VERCEL_ENV = "preview";
  const previewDevelop = (await getSpecVersions()).find((v) => v.id === "develop");
  assert.equal(previewDevelop.isCurrent, false);
  assert.equal(previewDevelop.origin, "https://ekgf.org/dprod");
  const previewResponse = await middleware(new NextRequest("https://preview.example/dprod/spec/develop/"));
  assert.equal(previewResponse.headers.get("location"), "https://ekgf.org/dprod/spec/");
});
