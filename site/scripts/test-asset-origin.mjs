import assert from "node:assert/strict";
import { test } from "node:test";

test("deployment builds keep browser assets on the requesting origin", async () => {
  process.env.VERCEL_URL = "dprod-enterprise-regression-ekgf.vercel.app";
  const { default: config } = await import("../next.config.ts");
  assert.equal(config.basePath, "/dprod");
  assert.ok(
    config.assetPrefix === undefined || config.assetPrefix === "/dprod",
    "CSS, JavaScript and fonts must use /dprod on the requesting origin",
  );
});
