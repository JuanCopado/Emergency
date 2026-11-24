"use strict";
/* Real-browser check of the lab page (Chromium, 360x640 and desktop). Usage: node e2e.cjs [screenshotDir]. Exit 1 on any failure. */
const fs = require("fs");
const path = require("path");
const assert = require("node:assert/strict");
const http = require("node:http");
const { chromium } = require("playwright");
const contract = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "..", "..", "references", "modality-abstention-layer7.contract.proposed.json"), "utf8"));
const TEXTS = contract["x-message-texts"];
// Some managed browsers prohibit file: navigation. Serve only these static lab
// assets on an ephemeral loopback port; never expose a repository file server.
const assets = new Map(["index.html", "fixtures.js", "ui-logic.js", "app.js"].map((name) =>
  ["/" + name, { bytes: fs.readFileSync(path.join(__dirname, name)), type: name.endsWith(".html") ? "text/html" : "text/javascript" }]));
let origin;
const server = http.createServer((req, res) => {
  const asset = assets.get(req.url);
  if (req.method !== "GET" || !asset) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "Content-Type": asset.type, "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff" });
  res.end(asset.bytes);
});
const shots = process.argv[2];

async function open(browser, viewport) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => { if (!r.url().startsWith(origin + "/") && !r.url().startsWith("blob:") && !r.url().startsWith("data:")) errors.push("external network request: " + r.url()); });
  await page.goto(origin + "/index.html");
  await page.waitForSelector("html[data-ready='1']");
  return { page, errors, ctx };
}
async function begin(page, arm, trial, lang) {
  await page.selectOption("#arm", arm); await page.selectOption("#trial", trial); await page.selectOption("#lang", lang);
  await page.click("#start");
}
const overflow = (page) => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);

(async () => {
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  origin = "http://127.0.0.1:" + server.address().port;
  let browser;
  const results = [];
  const check = (name, ok) => { results.push([name, ok]); if (!ok) process.exitCode = 1; };
  try {
    browser = await chromium.launch();
    for (const [width, height] of [[360, 640], [390, 844], [1280, 800]]) {
      const { page, errors, ctx } = await open(browser, { width, height });
      const label = `${width}x${height}`;
      // E1, arm B, per language: message text identical to the approved literal; send blocked; no force control.
      for (const lang of ["es", "pt", "en"]) {
        await begin(page, "B", "S1-14", lang);
        check(`${label} ${lang} E1 selector visible, banner present`, await page.isVisible("#selector") && (await page.textContent("#banner")).includes("SIMULATED_LAB_HARNESS_ONLY"));
        await page.click("#send");
        check(`${label} ${lang} E1 alert shown (T7-01)`, (await page.getAttribute("#alert", "data-trigger")) === "T7-01_UNDECLARED_MODALITY");
        check(`${label} ${lang} E1 text equals the approved literal`, (await page.textContent("#alert-text")) === TEXTS.MSG_T7_A[lang]);
        check(`${label} ${lang} E1 send disabled while blocked`, await page.isDisabled("#send"));
        const labels = (await page.$$eval("button", (bs) => bs.map((b) => b.textContent))).join("|");
        check(`${label} ${lang} no force-send control`, !/forzar|force|enviar de todos modos|send anyway|ignorar|ignore|omitir|skip/i.test(labels));
        check(`${label} ${lang} alert above the fold`, await page.$eval("#alert", (el) => el.getBoundingClientRect().top < window.innerHeight));
        check(`${label} ${lang} no horizontal overflow`, (await overflow(page)) <= 0);
        if (shots && lang === "es") await page.screenshot({ path: path.join(shots, `e1-${label}.png`), fullPage: true });
        await page.check("input[name=modality][value=ecg]");
        check(`${label} ${lang} recovery re-enables send`, !(await page.isDisabled("#send")));
        await page.click("#send");
        check(`${label} ${lang} simulated send completes`, await page.isVisible("#sentbox"));
        await page.click("#end");
        const out = await page.evaluate(() => window.__HF_EXPORT__());
        const types = out.events.map((e) => e.type);
        check(`${label} ${lang} events captured in order`, JSON.stringify(types) === JSON.stringify(["trial_start", "preview_shown", "send_attempt", "layer7_message_shown", "modality_selected", "recovery_action", "send_attempt", "send_simulated", "trial_end"]));
        check(`${label} ${lang} export labelled and without forced send`, out.label === "SIMULATED_LAYER7_HARNESS_LAB_ONLY" && out.layer7_execution_mode === "SIMULATED_LAB_HARNESS_ONLY" && out.forced_send_available === false);
        check(`${label} ${lang} no calendar time in export`, !/\d{4}-\d{2}-\d{2}/.test(JSON.stringify(out)));
      }
      // E2: corrupt JPEG (T7-03 -> Texto 3) and PDF to the photo route (T7-04 -> Texto 2); QA audio (Texto 4); recover by replacing the file.
      for (const [trial, message] of [["S1-15", "MSG_T7_C"], ["S2-15", "MSG_T7_B"], ["QA-01", "MSG_T7_D"]]) {
        await begin(page, "B", trial, "es");
        await page.click("#send");
        check(`${label} ${trial} text equals the approved literal`, (await page.textContent("#alert-text")) === TEXTS[message].es);
        check(`${label} ${trial} no overflow`, (await overflow(page)) <= 0);
        await page.click("#rec-file");
        await page.click("#send");
        check(`${label} ${trial} replacing the file lets the simulated send finish`, await page.isVisible("#sentbox"));
      }
      // Arm A mock: legacy behaviour, no selector, no Layer 7.
      await begin(page, "A", "S1-15", "es");
      check(`${label} arm A has no selector`, !(await page.isVisible("#selector")));
      await page.click("#send");
      check(`${label} arm A has no Layer 7 message`, !(await page.isVisible("#alert")) && await page.isVisible("#sentbox"));
      check(`${label} arm A labelled not applicable`, (await page.getAttribute("#lab", "data-layer7-execution-mode")) === "NOT_APPLICABLE_ARM_A");
      check(`${label} no page errors and no external network`, errors.length === 0);
      await ctx.close();
    }
  } finally {
    try { if (browser) await browser.close(); }
    finally { await new Promise((resolve) => server.close(resolve)); }
  }
  const failed = results.filter(([, ok]) => !ok);
  console.log(JSON.stringify({ checks: results.length, failed: failed.map(([n]) => n) }));
})().catch((e) => { console.error(e); process.exit(1); });
