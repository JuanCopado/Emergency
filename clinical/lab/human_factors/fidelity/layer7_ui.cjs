"use strict";
/* R28 · Layer 7 UI of arm B observed in the REAL app (VITE_R51_PROTOTYPE=1 and VITE_LAB_LAYER7=1, dev server only). LABORATORY ONLY.
 * The banner is rendered by the app's own lab component (app/src/lab/LabModalityEntry.tsx); this runner only answers the two lab
 * endpoints: /api/lab/layer7/evaluate (layer7_adapter.py -> R22 harness over the inactive contract) and /upload/prepare (real dispatch).
 * Scenarios are driven through the UI as a person would; nothing is generated outside the screen. SYNTHETIC technical driver, no people.
 * Usage: node layer7_ui.cjs <appDir> <out.json> */
const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn, execFileSync } = require("child_process");
const { chromium } = require("playwright");

const [appDir, outFile] = process.argv.slice(2);
if (!appDir || !outFile) { console.error("usage: node layer7_ui.cjs <appDir> <out.json>"); process.exit(2); }
const HERE = __dirname;
const STIMULI = path.join(HERE, "..", "bank", "stimuli");
const MIME = { ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".wav": "audio/wav" };
const LANGS = ["es", "pt", "en"];
const VIEWPORTS = [{ width: 360, height: 640 }, { width: 390, height: 844 }];
const FORCE = /forçar|forzar|force|enviar mesmo|enviar de todos modos|send anyway/i;

const run = (script, input) => JSON.parse(execFileSync("python3", ["-I", script], { input: JSON.stringify(input) }).toString());
const realPrepare = (body) => run(path.join(HERE, "prepare_stub.py"), { path: "/api/clinical-note/upload/prepare", payload: body });
const evaluate = (req) => run(path.join(HERE, "..", "layer7_adapter.py"), req);
const freePort = () => new Promise((res, rej) => { const p = require("net").createServer(); p.on("error", rej); p.listen(0, "127.0.0.1", () => { const { port } = p.address(); p.close(() => res(port)); }); });
async function startVite(env) {
  const port = await freePort();
  const child = spawn("npx", ["vite", "--port", String(port), "--strictPort", "--host", "127.0.0.1"], { cwd: appDir, env: { ...process.env, ...env }, stdio: "ignore" });
  const url = "http://127.0.0.1:" + port;
  for (let i = 0; i < 90; i++) {
    try { await new Promise((ok, no) => http.get(url, (r) => { r.resume(); ok(); }).on("error", no)); return { url, close: () => child.kill("SIGTERM") }; } catch { await new Promise((r) => setTimeout(r, 1000)); }
  }
  child.kill("SIGTERM"); throw new Error("vite did not start");
}
async function openMcdt(page) {
  const tabs = page.locator("button").filter({ hasText: /^(Historia|História|History|病史)/ });
  await (await tabs.first().elementHandle()).evaluate((el) => el.parentElement.children[2].click());
}

const SCENARIOS = [
  { id: "E1_T7-01_file_before_modality", entry: "e1", file: "S2-14.pdf", expect: "T7-01_UNDECLARED_MODALITY", recover: "ECG" },
  { id: "E2_T7-03_corrupt_jpeg", file: "S1-15.jpg", modality: /Pele|Piel|Skin|Wound/i, expect: "T7-03_CORRUPT_UNPROCESSABLE" },
  { id: "E2_T7-04_pdf_on_photo_route", file: "S2-15.pdf", modality: /Pele|Piel|Skin|Wound/i, expect: "T7-04_FORMAT_CONTAINER_MISMATCH" },
  { id: "E2_T7-04_audio_global_format", file: "QA-01.wav", modality: /Pele|Piel|Skin|Wound/i, expect: "T7-04_FORMAT_CONTAINER_MISMATCH" },
  { id: "F_document_kind_null_selected", file: "S1-13.pdf", modality: /Document/i, expect: null },
  { id: "F_valid_rgb_ecg", file: "S1-14.png", modality: /ECG/i, expect: null },
];

async function trial(browser, baseUrl, lang, vp, sc) {
  const ctx = await browser.newContext({ viewport: vp });
  await ctx.addInitScript((l) => { try { localStorage.setItem("emergency.lang", l); } catch (e) {} }, lang);
  const page = await ctx.newPage();
  const verdicts = []; let realPrepareCalls = 0;
  await page.route("**/api/**", async (route) => {
    const url = route.request().url();
    if (url.endsWith("/api/lab/layer7/evaluate")) { const v = evaluate(JSON.parse(route.request().postData())); verdicts.push(v); return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(v) }); }
    if (url.endsWith("/api/clinical-note/upload/prepare")) { realPrepareCalls += 1; const r = realPrepare(JSON.parse(route.request().postData())); return route.fulfill({ status: r.status, contentType: "application/json", body: JSON.stringify(r.body) }); }
    return route.fulfill({ status: 503, contentType: "application/json", body: "{}" });
  });
  await page.goto(baseUrl + "/clinical-note" + (sc.entry ? "?lab_entry=" + sc.entry : ""), { waitUntil: "networkidle" });
  await openMcdt(page);
  const entry = page.getByTestId("r51-modality-entry");
  await entry.waitFor();
  const fileInputBefore = await page.locator("input[type=file]").count();       // E1: present before any modality; other trials: absent
  if (sc.modality) await entry.getByRole("button", { name: sc.modality }).first().click();
  const buffer = fs.readFileSync(path.join(STIMULI, sc.file));
  await page.locator("input[type=file]").first().setInputFiles({ name: sc.file, mimeType: MIME[path.extname(sc.file)] || "application/octet-stream", buffer });
  const banner = page.getByTestId("lab-layer7-banner");
  await page.waitForTimeout(1200);
  const shown = (await banner.count()) > 0;
  const out = { scenario: sc.id, language: lang, viewport: vp.width, expected_trigger: sc.expect, adapter_trigger: verdicts.length ? verdicts[verdicts.length - 1].trigger_id : null,
    file_input_present_before_modality: fileInputBefore > 0, banner_shown: shown };
  if (shown) {
    const box = await banner.boundingBox();
    const text = (await banner.innerText()).trim();
    const v = verdicts[verdicts.length - 1];
    const controls = await banner.getByRole("button").allInnerTexts();
    Object.assign(out, { text_equals_adapter_text: text.startsWith(v.message_text.trim()), role_alert: (await banner.getAttribute("role")) === "alert", aria_live: await banner.getAttribute("aria-live"),
      focused: await banner.evaluate((el) => document.activeElement === el), above_fold: box.y + box.height <= vp.height, fully_in_viewport_width: box.x >= 0 && box.x + box.width <= vp.width,
      recovery_controls: controls, force_send_controls: await page.getByRole("button", { name: FORCE }).count(), confirm_buttons: await page.getByRole("button", { name: /Confirmar|Confirm/ }).count() });
    if (sc.recover) {
      await entry.getByRole("button", { name: new RegExp("^" + sc.recover + "$", "i") }).first().click();
      await page.waitForTimeout(1200);
      out.recovered_after_modality_choice = (await banner.count()) === 0 && (await page.getByRole("button", { name: /Confirmar|Confirm/ }).count()) > 0;
    }
  } else {
    await page.getByRole("button", { name: /Confirmar|Confirm/ }).first().click();
    await page.waitForTimeout(900);
    out.review_card_created = (await page.getByTestId("mcdt-review-card").count()) > 0;
  }
  out.overflow_px = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  out.lab_log_events = await page.evaluate(() => (window.__LAB_LAYER7_LOG__ || []).map((e) => e.type));
  out.real_prepare_calls = realPrepareCalls;
  await ctx.close();
  return out;
}

(async () => {
  const dev = await startVite({ VITE_R51_PROTOTYPE: "1", VITE_LAB_LAYER7: "1" });
  const browser = await chromium.launch();
  const w = await browser.newPage();
  await w.goto(dev.url + "/clinical-note", { waitUntil: "networkidle" }).catch(() => {}); await w.waitForTimeout(4000); await w.reload({ waitUntil: "networkidle" }).catch(() => {}); await w.close();
  const results = [];
  try { for (const lang of LANGS) for (const vp of VIEWPORTS) for (const sc of SCENARIOS) results.push(await trial(browser, dev.url, lang, vp, sc)); }
  finally { await browser.close(); dev.close(); }
  const abst = results.filter((r) => r.expected_trigger);
  const valid = results.filter((r) => !r.expected_trigger);
  const summary = {
    trials: results.length,
    abstentions_as_expected: abst.every((r) => r.adapter_trigger === r.expected_trigger && r.banner_shown && r.text_equals_adapter_text && r.role_alert && r.aria_live === "assertive" && r.focused && r.force_send_controls === 0 && r.confirm_buttons === 0),
    banner_above_fold_everywhere: abst.every((r) => r.above_fold), banner_inside_viewport_width_everywhere: abst.every((r) => r.fully_in_viewport_width), no_horizontal_overflow: results.every((r) => r.overflow_px <= 0),
    e1_file_input_before_modality: results.filter((r) => r.scenario.startsWith("E1")).every((r) => r.file_input_present_before_modality),
    other_trials_keep_approved_flow: results.filter((r) => !r.scenario.startsWith("E1")).every((r) => !r.file_input_present_before_modality),
    e1_recovery_by_choosing_modality: results.filter((r) => r.scenario.startsWith("E1")).every((r) => r.recovered_after_modality_choice === true),
    valid_trials_not_blocked: valid.every((r) => !r.banner_shown && r.review_card_created === true),
    languages: LANGS, viewports: VIEWPORTS.map((v) => v.width), contrast_measured: false, screen_reader_tested: false, edge_checked: false,
    execution_mode: "SYNTHETIC_TECHNICAL_DRIVER_ON_REAL_APP_LAB_BUILD_ONLY", study_with_humans: "NOT_AUTHORISED",
  };
  fs.writeFileSync(outFile, JSON.stringify({ tool: "layer7_ui.cjs", summary, results }, null, 1) + "\n");
  console.log(JSON.stringify(summary));
})().catch((e) => { console.error(e); process.exit(1); });
