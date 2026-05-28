#!/usr/bin/env node
// Compiles src/ts/{filter,theme}.ts → static/{filter,theme}.js as IIFE
// bundles (vanilla, no runtime dependencies). Run by `pnpm run build:js`
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
    resolve(root, "src/ts/theme.ts"),
  ],
  outdir: resolve(root, "static"),
  bundle: true,
  format: "iife",
  target: ["es2017"],
  sourcemap: true,
  legalComments: "none",
  logLevel: "info",
  define: { "process.env.NODE_ENV": '"production"' },
};

const watch = process.argv.includes("--watch");

if (watch) {
  const ctx = await context(baseOptions);
  await ctx.watch();
  console.log("[build-js] watching src/ts/*.ts …");
} else {
  await build(baseOptions);
  console.log("[build-js] compiled static/filter.js + static/theme.js");
}
