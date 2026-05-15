#!/usr/bin/env node
// Compiles src/ts/{filter,tweaks}.ts → static/{filter,tweaks}.js as IIFE
// bundles with jQuery treated as a global ($). Run by `pnpm run build:js`
// and invoked from the Python build pipeline.

import { build, context } from "esbuild";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");

/** @type {import('esbuild').BuildOptions} */
const baseOptions = {
  entryPoints: [
    resolve(root, "src/ts/filter.ts"),
    resolve(root, "src/ts/tweaks.ts"),
  ],
  outdir: resolve(root, "static"),
  bundle: true,
  format: "iife",
  target: ["es2017"],
  sourcemap: true,
  legalComments: "none",
  logLevel: "info",
  // jQuery loaded from CDN as a global — don't try to resolve it.
  external: ["jquery"],
  define: { "process.env.NODE_ENV": '"production"' },
};

const watch = process.argv.includes("--watch");

if (watch) {
  const ctx = await context(baseOptions);
  await ctx.watch();
  console.log("[build-js] watching src/ts/*.ts …");
} else {
  await build(baseOptions);
  console.log("[build-js] compiled static/filter.js + static/tweaks.js");
}
