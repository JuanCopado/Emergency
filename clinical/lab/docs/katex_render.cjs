"use strict";
// Renders math with KaTeX (server side). stdin: JSON [[tex, display], ...] -> stdout: JSON [html|null, ...]. Needs --katex-dir <dir containing node_modules/katex>.
const path = require("path");
const idx = process.argv.indexOf("--katex-dir");
if (idx < 0) { console.error("missing --katex-dir"); process.exit(2); }
const katex = require(path.join(path.resolve(process.argv[idx + 1]), "node_modules", "katex"));
let input = "";
process.stdin.on("data", (c) => (input += c)).on("end", () => {
  const out = JSON.parse(input).map(([tex, display]) => {
    try { return katex.renderToString(tex, { displayMode: !!display, throwOnError: true, output: "html", strict: "error" }); }
    catch (e) { return null; }
  });
  process.stdout.write(JSON.stringify(out));
});
