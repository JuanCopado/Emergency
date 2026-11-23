"use strict";
// HTML -> PDF with Chromium (Playwright) plus DOM-level layout checks. Usage: node render_pdf.cjs in.html out.pdf
const path = require("path");
const { chromium } = require("playwright");
(async () => {
  const [input, output] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + path.resolve(input));
  await page.evaluate(() => document.fonts.ready);
  const checks = await page.evaluate(() => {
    const overflowTables = [...document.querySelectorAll("table")].filter((t) => t.scrollWidth > t.parentElement.clientWidth + 1).length;
    const tables = document.querySelectorAll("table").length;
    const katexErrors = document.querySelectorAll(".katex-error").length;
    const text = document.body.innerText;
    const rawMath = (text.match(/\\(?:frac|hat|times|text|sum|Delta|rho|ge|le|qquad|mathbb|begin)\b|\$[^$\n]{1,80}\$/g) || []).length;
    const wideCells = [...document.querySelectorAll("td,th")].filter((c) => c.scrollWidth > c.clientWidth + 1).length;
    return { tables, overflowTables, katexErrors, rawMathTokens: rawMath, overflowingCells: wideCells, math: document.querySelectorAll(".katex").length };
  });
  await page.pdf({ path: output, format: "A4", printBackground: true, displayHeaderFooter: true, preferCSSPageSize: true,
    headerTemplate: "<span></span>", footerTemplate: '<div style="font-size:7pt;width:100%;text-align:center;color:#555"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  await browser.close();
  console.log(JSON.stringify(checks));
})().catch((e) => { console.error(e); process.exit(1); });
