"use strict";
/* R26 · REAL arms A/B for the human-factors laboratory (no mock-up). LABORATORY ONLY, never imported by the product.
 *   P_prod : production build of the app (reference, flag OFF).
 *   A_dev  : the SAME app source served by the Vite dev server with the R5-1 flag OFF  -> arm A (control).
 *   B_dev  : the SAME app source served by the Vite dev server with VITE_R51_PROTOTYPE=1 -> arm B selector (R5-1 layers 1-6).
 * The R5-1 prototype is ignored by production builds on purpose (r51PrototypeEnabled needs !PROD), so both arms use the dev server:
 * identical infrastructure. Only /upload/prepare is answered, with the REAL server dispatch (prepare_stub.py); nothing else leaves the page.
 * Layer 7: the app has NO Layer 7 UI, so arm B here lacks the abstention messages (reported as BLOCKED, not simulated by this tool).
 * Usage: node real_arms.cjs <appDir> <productionBuildDir> <out.json> */
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn, execFileSync } = require("child_process");
const { chromium } = require("playwright");

const [appDir, prodDir, outFile] = process.argv.slice(2);
if (!appDir || !prodDir || !outFile) { console.error("usage: node real_arms.cjs <appDir> <productionBuildDir> <out.json>"); process.exit(2); }
const HERE = __dirname;
const STIMULI = path.join(HERE, "..", "bank", "stimuli");
const MIME = { ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp" };
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".webmanifest": "application/manifest+json" };
const VIEWPORTS = [{ width: 360, height: 640 }, { width: 1280, height: 800 }];
const LANGS = ["es", "pt", "en"];
const SCENARIOS = { document: { file: "S1-13.pdf", modality: /Document/i }, image: { file: "S1-14.png", modality: /Pele|Piel|Skin|Wound/i } };

function realPrepare(body) {
  const out = execFileSync("python3", ["-I", path.join(HERE, "prepare_stub.py")], { input: JSON.stringify({ path: "/api/clinical-note/upload/prepare", payload: body }) });
  return JSON.parse(out.toString());
}
function serveStatic(dir) {
  const server = http.createServer((req, res) => {
    let file = path.join(dir, decodeURIComponent(req.url.split("?")[0]));
    if (!file.startsWith(path.resolve(dir)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(dir, "index.html");
    res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
    res.end(fs.readFileSync(file));
  });
  return new Promise((r) => server.listen(0, "127.0.0.1", () => r({ url: "http://127.0.0.1:" + server.address().port, close: () => server.close() })));
}
async function startVite(env) {
  const port = 20000 + Math.floor(Math.random() * 20000);
  const child = spawn("npx", ["vite", "--port", String(port), "--strictPort", "--host", "127.0.0.1"], { cwd: appDir, env: { ...process.env, ...env }, stdio: "ignore" });
  const url = "http://127.0.0.1:" + port;
  for (let i = 0; i < 90; i++) {
    try { await new Promise((ok, no) => http.get(url, (r) => { r.resume(); ok(); }).on("error", no)); return { url, close: () => child.kill("SIGTERM") }; } catch { await new Promise((r) => setTimeout(r, 500)); }
  }
  child.kill("SIGTERM"); throw new Error("vite did not start");
}

async function openMcdt(page) {
  const tabs = page.locator("button").filter({ hasText: /^(Historia|História|History|病史)/ });
  await (await tabs.first().elementHandle()).evaluate((el) => el.parentElement.children[2].click());
}
async function controls(page) {
  return page.evaluate(() => {
    const root = document.querySelector("[data-testid=r51-modality-entry]") ? document.querySelector("[data-testid=r51-modality-entry]").parentElement.parentElement : Array.from(document.querySelectorAll("section")).find((s) => s.querySelector("input[type=file]"));
    return Array.from(root.querySelectorAll("button,input,textarea,select")).filter((e) => e.offsetParent).map((e) => {
      const r = e.getBoundingClientRect();
      return { role: e.tagName.toLowerCase() + (e.type ? ":" + e.type : ""), name: (e.getAttribute("aria-label") || e.textContent || e.placeholder || "").trim().slice(0, 60), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) };
    });
  });
}
async function runTrial(browser, baseUrl, vp, lang, scenario, arm) {
  const ctx = await browser.newContext({ viewport: vp });
  await ctx.addInitScript((l) => { try { localStorage.setItem("emergency.lang", l); } catch (e) {} }, lang);
  const page = await ctx.newPage();
  let prepareCalls = 0, explicitKind = "unset";
  await page.route("**/api/**", async (route) => {
    if (!route.request().url().endsWith("/api/clinical-note/upload/prepare")) return route.abort();
    prepareCalls += 1;
    const body = JSON.parse(route.request().postData()); explicitKind = body.explicit_kind === undefined ? null : body.explicit_kind;
    const r = realPrepare(body);
    await route.fulfill({ status: r.status, contentType: "application/json", body: JSON.stringify(r.body) });
  });
  await page.goto(baseUrl + "/clinical-note", { waitUntil: "networkidle" });
  let actions = 0;
  await openMcdt(page); actions += 1;
  const before = await controls(page);
  const overflow = await page.evaluate(() => Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth));
  const sc = SCENARIOS[scenario];
  const buffer = fs.readFileSync(path.join(STIMULI, sc.file));
  const file = { name: sc.file, mimeType: MIME[path.extname(sc.file)], buffer };
  let t0;
  if (arm === "B") {
    await page.getByTestId("r51-modality-entry").getByRole("button", { name: sc.modality }).first().click(); actions += 1;
    await page.locator("input[type=file]").first().setInputFiles(file); actions += 1;
    t0 = Date.now();
    await page.getByRole("button", { name: /Confirmar|Confirm/ }).first().click(); actions += 1;
  } else {
    t0 = Date.now();
    await page.locator("input[type=file]").first().setInputFiles(file); actions += 1;
  }
  const card = page.getByTestId("mcdt-review-card");
  await card.first().waitFor({ timeout: 15000 }).catch(() => {});
  const latency = Date.now() - t0;
  const hasCard = (await card.count()) > 0;
  const text = hasCard ? (await card.first().innerText()).replace(/\s+/g, " ") : null;
  await ctx.close();
  return { controls_before: before, overflow_px: overflow, minimum_actions_to_review_card: actions, prepare_calls: prepareCalls, explicit_kind_sent: explicitKind, review_card: hasCard, card_text: text, latency_ms: latency };
}

function compare(a, p) {
  const out = { same_control_names_and_order: JSON.stringify(a.controls_before.map((c) => [c.role, c.name])) === JSON.stringify(p.controls_before.map((c) => [c.role, c.name])), max_box_delta_px: null, same_card_text: a.card_text === p.card_text, same_actions: a.minimum_actions_to_review_card === p.minimum_actions_to_review_card, overflow_px: [a.overflow_px, p.overflow_px], latency_delta_ms: Math.abs(a.latency_ms - p.latency_ms) };
  if (a.controls_before.length === p.controls_before.length) out.max_box_delta_px = Math.max(0, ...a.controls_before.map((c, i) => Math.max(Math.abs(c.x - p.controls_before[i].x), Math.abs(c.y - p.controls_before[i].y), Math.abs(c.w - p.controls_before[i].w), Math.abs(c.h - p.controls_before[i].h))));
  return out;
}

(async () => {
  const prod = await serveStatic(prodDir);
  const dev = { A: await startVite({}), B: await startVite({ VITE_R51_PROTOTYPE: "1" }) };
  const browser = await chromium.launch();
  for (const server of [dev.A, dev.B]) {          // warm-up: the dev server may reload the page once while it optimizes dependencies
    const w = await browser.newPage();
    await w.goto(server.url + "/clinical-note", { waitUntil: "networkidle" }).catch(() => {});
    await w.waitForTimeout(4000); await w.reload({ waitUntil: "networkidle" }).catch(() => {}); await w.close();
  }
  const runs = [];
  try {
    for (const lang of LANGS) for (const vp of VIEWPORTS) for (const scenario of Object.keys(SCENARIOS)) {
      const P = await runTrial(browser, prod.url, vp, lang, scenario, "A");
      const A = await runTrial(browser, dev.A.url, vp, lang, scenario, "A");
      const B = await runTrial(browser, dev.B.url, vp, lang, scenario, "B").catch((e) => { throw new Error("arm B failed at " + lang + " " + vp.width + " " + scenario + ": " + String(e.message).split("\n")[0]); });
      runs.push({ lang, viewport: vp, scenario, P_prod: P, A_dev: A, B_dev: B, A_vs_prod: compare(A, P) });
    }
  } finally { await browser.close(); dev.A.close(); dev.B.close(); prod.close(); }
  const aVsProd = runs.map((r) => r.A_vs_prod);
  const summary = {
    arm_a_equals_production_everywhere: aVsProd.every((c) => c.same_control_names_and_order && c.same_card_text && c.same_actions && (c.max_box_delta_px === null || c.max_box_delta_px <= 4) && c.overflow_px[0] === c.overflow_px[1]),
    arm_a_max_box_delta_px: Math.max(...aVsProd.map((c) => c.max_box_delta_px || 0)),
    arm_a_max_latency_delta_ms: Math.max(...aVsProd.map((c) => c.latency_delta_ms)),
    arm_b_extra_actions_vs_a: [...new Set(runs.map((r) => r.B_dev.minimum_actions_to_review_card - r.A_dev.minimum_actions_to_review_card))],
    arm_b_layer7_abstention_ui: "BLOCKED: the app has no Layer 7 UI; adding it is an app change (see R26 report)",
    browser: "chromium " + (await chromium.launch().then(async (b) => { const v = b.version(); await b.close(); return v; })), edge_checked: false,
  };
  fs.writeFileSync(outFile, JSON.stringify({ tool: "real_arms.cjs", variants: { P_prod: "production build, flag OFF", A_dev: "dev server, flag OFF (arm A)", B_dev: "dev server, VITE_R51_PROTOTYPE=1 (arm B selector)" }, summary, runs }, null, 1) + "\n");
  console.log(JSON.stringify(summary));
})().catch((e) => { console.error(e); process.exit(1); });
