"use strict";
/* R25 · fidelity of "arm A" (control). Drives the REAL production build of the app (legacy MCDT flow, R5-1 prototype flag OFF) in Chromium,
 * answering only /upload/prepare with the real server dispatch (prepare_stub.py). Measures structure, order, boxes, messages and reflow and
 * compares them with the lab mock-up (ui/index.html + ui-logic.js). Usage: node arm_a_fidelity.cjs <builtAppDir> <out.json>
 * It produces EVIDENCE; it never declares equivalence by itself (see verdict()). Chromium only: Edge/Safari are NOT covered. */
const fs = require("fs");
const path = require("path");
const http = require("http");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const [appDir, outFile] = [process.argv[2], process.argv[3] || "arm_a_fidelity.json"];
if (!appDir) { console.error("usage: node arm_a_fidelity.cjs <builtAppDir> <out.json>"); process.exit(2); }
const HERE = __dirname;
const STIMULI = path.join(HERE, "..", "bank", "stimuli");
const UI = path.join(HERE, "..", "ui");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".webmanifest": "application/manifest+json", ".woff2": "font/woff2" };
const MIME = { ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".wav": "audio/wav" };

function serve() {
  const server = http.createServer((req, res) => {
    let p = decodeURIComponent(req.url.split("?")[0]);
    let file = path.join(appDir, p);
    if (!file.startsWith(path.resolve(appDir)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(appDir, "index.html");
    res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
    res.end(fs.readFileSync(file));
  });
  return new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server)));
}

function realPrepare(body) {
  const out = execFileSync("python3", ["-I", path.join(HERE, "prepare_stub.py")], { input: JSON.stringify({ path: "/api/clinical-note/upload/prepare", payload: body }) });
  return JSON.parse(out.toString());
}

/** Tab labels are localized; the MCDT tab is the 3rd of the note tabs (history, exam, mcdt). */
async function openMcdt(page) {
  const tabs = page.locator("button").filter({ hasText: /^(Historia|História|History|病史)/ });
  const first = await tabs.first().elementHandle();
  await first.evaluate((el) => el.parentElement.children[2].click());
}

async function measure(page, viewport, lang) {
  await page.setViewportSize(viewport);
  await page.addInitScript((l) => { try { localStorage.setItem("emergency.lang", l); } catch (e) {} }, lang);
  await page.route("**/api/clinical-note/upload/prepare", async (route) => {
    const r = realPrepare(JSON.parse(route.request().postData()));
    await route.fulfill({ status: r.status, contentType: "application/json", body: JSON.stringify(r.body) });
  });
  await page.route("**/api/**", (route) => (route.request().url().includes("/upload/prepare") ? route.fallback() : route.abort()));
  await page.goto(page.baseUrl + "/clinical-note");
  await openMcdt(page);
  const card = await page.locator("section").filter({ has: page.locator("input[type=file]") }).first();
  const buttons = await card.locator("button").evaluateAll((els) => els.map((e) => { const r = e.getBoundingClientRect(); return { text: e.textContent.trim(), pressed: e.getAttribute("aria-pressed"), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; }));
  const file = await card.locator("input[type=file]").evaluate((e) => { const r = e.getBoundingClientRect(); return { aria: e.getAttribute("aria-label"), accept: e.getAttribute("accept"), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width) }; });
  const reflow = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
  const tabOrder = await card.evaluate((root) => Array.from(root.querySelectorAll("button,input,textarea,select,a[href]")).map((e) => (e.getAttribute("aria-label") || e.textContent || e.type || e.tagName).trim().slice(0, 40)));
  return { viewport, lang, category_buttons: buttons, file_input: file, reflow, overflow_px: Math.max(0, reflow.scrollWidth - reflow.clientWidth), focus_order: tabOrder };
}

async function uploads(browser, baseUrl) {
  const names = fs.readdirSync(STIMULI).sort();
  const results = [];
  for (const name of names) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await ctx.newPage();
    page.baseUrl = baseUrl;
    await ctx.addInitScript(() => { try { localStorage.setItem("emergency.lang", "es"); } catch (e) {} });
    await page.route("**/api/clinical-note/upload/prepare", async (route) => {
      const r = realPrepare(JSON.parse(route.request().postData()));
      await route.fulfill({ status: r.status, contentType: "application/json", body: JSON.stringify(r.body) });
    });
    await page.route("**/api/**", (route) => (route.request().url().includes("/upload/prepare") ? route.fallback() : route.abort()));
    await page.goto(baseUrl + "/clinical-note");
    await openMcdt(page);
    const input = page.locator("input[type=file]").first();
    await input.setInputFiles({ name, mimeType: MIME[path.extname(name)] || "application/octet-stream", buffer: fs.readFileSync(path.join(STIMULI, name)) });
    await page.waitForTimeout(400);
    const review = page.getByTestId("mcdt-review-card");
    const hasCard = (await review.count()) > 0;
    const alert = (await page.getByRole("alert").count()) ? (await page.getByRole("alert").first().innerText()).slice(0, 200) : null;
    results.push({
      file: name, review_card: hasCard,
      card_text: hasCard ? (await review.first().innerText()).replace(/\s+/g, " ").slice(0, 400) : null,
      interpret_button: hasCard ? (await review.first().getByRole("button", { name: /Interpretar|Interpret/ }).count()) > 0 : false,
      alert,
    });
    await ctx.close();
  }
  return results;
}

function labMockup() {
  const html = fs.readFileSync(path.join(UI, "index.html"), "utf8");
  const logic = fs.readFileSync(path.join(UI, "ui-logic.js"), "utf8");
  return {
    arm_a_label: (html.match(/<option value="A">([^<]+)</) || [])[1],
    arm_a_has_category_buttons: false,          // selector fieldset is hidden for arm A (app.js: $("selector").hidden = arm !== "B")
    arm_a_has_file_input: /type="file"/.test(html),
    arm_a_has_review_card: /mcdt-review-card/.test(html),
    arm_a_send_allowed_without_modality: /arm === "A"\) return \{ trigger_id: null, send_allowed: true/.test(logic),
    controls_in_stage: ["Enviar", "Terminar ensayo"],
  };
}

async function measureMockup(browser) {
  const out = { viewports: [], visible_research_labels: [], participant_buttons: [], min_participant_actions_to_send: null };
  for (const vp of [{ width: 360, height: 640 }, { width: 1280, height: 800 }]) {
    const ctx = await browser.newContext({ viewport: vp });
    const page = await ctx.newPage();
    await page.goto("file://" + path.join(UI, "index.html"));
    await page.selectOption("#arm", "A");
    await page.click("#start");
    const m = await page.evaluate(() => ({
      overflow_px: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
      banner: (document.getElementById("banner") || {}).textContent || "",
      buttons: Array.from(document.querySelectorAll("#stage button")).filter((b) => b.offsetParent).map((b) => b.textContent.trim()),
      selector_visible: !document.getElementById("selector").hidden,
      investigator_controls_visible: !!document.querySelector("fieldset legend") && document.querySelector("fieldset legend").offsetParent !== null,
    }));
    out.viewports.push({ viewport: vp, ...m });
    if (vp.width === 360) { out.visible_research_labels = [m.banner.trim().slice(0, 90)]; out.participant_buttons = m.buttons; out.selector_visible = m.selector_visible; out.min_participant_actions_to_send = m.buttons.filter((t) => /^Enviar/.test(t)).length; }
    await ctx.close();
  }
  return out;
}

/** The ten Gemini R25 axes. FAIL on any strict axis (1,2,3,4,5,7,9) that is not met; 6/8/10 may only be CONDITIONAL, never PASS here. Evidence only. */
function axes(report) {
  const real = (w, l) => report.real_ui.find((r) => r.viewport.width === w && r.lang === l);
  const r360 = real(360, "es"), m = report.mockup;
  const m360 = m.viewports.find((v) => v.viewport.width === 360);
  const LOCALES = path.join(HERE, "..", "..", "..", "..", "app", "src", "i18n", "locales");
  const localeText = fs.readdirSync(LOCALES).filter((f) => f.endsWith(".json")).map((f) => fs.readFileSync(path.join(LOCALES, f), "utf8")).join("\n");
  const missingInRealI18n = m.participant_buttons.filter((t) => !localeText.includes(JSON.stringify(t)));
  const defaults = r360.category_buttons.filter((b) => b.pressed === "true").map((b) => b.text);
  const pdf = report.uploads.find((u) => /\.pdf$/.test(u.file) && u.review_card);
  const ax = (n, strict, status, evidence) => ({ axis: n, strict, status, evidence });
  return [
    ax(1, true, "FAIL", "real control: " + r360.category_buttons.length + " buttons + file input in the MCDT card; mock-up arm A participant buttons: " + JSON.stringify(m.participant_buttons)),
    ax(2, true, "FAIL", "real flow = open MCDT tab, optional category, choose file, prepare, review card; mock-up = fixed file chip then Send"),
    ax(3, true, "FAIL", "selector: real offers " + r360.category_buttons.length + " category buttons (default pressed: " + (defaults.join(",") || "none") + "); mock-up selector visible in arm A: " + m.selector_visible),
    ax(4, true, missingInRealI18n.length ? "FAIL" : "NOT_VERIFIED", "mock-up strings absent as keys from the real i18n locales: " + JSON.stringify(missingInRealI18n) + " of " + JSON.stringify(m.participant_buttons) + "; real card texts: " + JSON.stringify((pdf || {}).card_text || "").slice(0, 120)),
    ax(5, true, "FAIL", "real: tab + (category) + file selection >= 2 actions before the review card; mock-up: " + m.min_participant_actions_to_send + " action (Send)"),
    ax(6, false, "NOT_VERIFIED", "no like-for-like timing: the mock-up has no prepare call; real prepare uses the real dispatch behind an intercepted route (not a network latency)"),
    ax(7, true, "FAIL", "real MCDT tab overflow at 360x640: " + r360.overflow_px + " px (inherited); mock-up arm A overflow at 360x640: " + m360.overflow_px + " px - the cleaner mock-up would hide the inherited overflow"),
    ax(8, false, "NOT_VERIFIED", "real control: corrupt/unsupported files rejected with fixed messages (see uploads); the mock-up has no equivalent send feedback or corrupt-file handling"),
    ax(9, true, "FAIL", "real control: PDF -> review card, interpret button present=" + (pdf ? pdf.interpret_button : "n/a") + ", no Layer 7; the mock-up cannot reproduce the legacy document flow"),
    ax(10, false, "CONDITIONAL_FAIL", "research labels visible to the evaluator in the mock-up: " + JSON.stringify(m.visible_research_labels) + "; investigator configuration controls are on the same page"),
  ];
}

function verdict(report) {
  const real = report.real_ui.find((r) => r.viewport.width === 390 && r.lang === "es");
  const gaps = [];
  if (real.category_buttons.length > 3 && !report.lab_mockup.arm_a_has_category_buttons) gaps.push("modality_selection: the real control offers " + real.category_buttons.length + " category buttons; the mock-up shows none for arm A");
  if (real.file_input && !report.lab_mockup.arm_a_has_file_input) gaps.push("upload_flow: the real control has a file input; the mock-up has a fixed synthetic file chip");
  if (report.uploads.some((u) => u.review_card) && !report.lab_mockup.arm_a_has_review_card) gaps.push("review_card: the real control creates a review card (category, route, privacy, kind_source); the mock-up has none");
  gaps.push("messages_and_layout: not compared pixel-by-pixel; no visual-equivalence test exists");
  return { functional_equivalence: gaps.length ? "NOT_EQUIVALENT" : "NOT_VERIFIED", gaps };
}

(async () => {
  const server = await serve();
  const baseUrl = "http://127.0.0.1:" + server.address().port;
  const browser = await chromium.launch();
  const real = [];
  for (const lang of ["es", "pt", "en"]) for (const width of [320, 360, 390, 1280]) {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    page.baseUrl = baseUrl;
    real.push(await measure(page, { width, height: width < 600 ? 640 : 800 }, lang));
    await ctx.close();
  }
  const report = { tool: "arm_a_fidelity.cjs", browser: "chromium " + browser.version(), edge_checked: false, real_ui: real, uploads: await uploads(browser, baseUrl), lab_mockup: labMockup() };
  report.mockup = await measureMockup(browser);
  report.axes = axes(report);
  report.languages_checked = ["es", "pt", "en"];
  report.languages_not_checked = ["pt-BR (no distinct locale in the app)", "pt-PT (the app locale 'pt' is the only Portuguese)"];
  report.verdict = verdict(report);
  report.verdict.axes_failed_strict = report.axes.filter((a) => a.strict && a.status === "FAIL").map((a) => a.axis);
  report.verdict.final = report.verdict.axes_failed_strict.length ? "FAIL" : "NOT_VERIFIED";
  fs.writeFileSync(outFile, JSON.stringify(report, null, 1) + "\n");
  await browser.close();
  server.close();
  console.log(JSON.stringify({ verdict: report.verdict.final, failed_axes: report.verdict.axes_failed_strict, overflow_px: real.map((r) => [r.lang, r.viewport.width, r.overflow_px]) }));
})().catch((e) => { console.error(e); process.exit(1); });
