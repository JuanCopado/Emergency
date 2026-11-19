import assert from 'node:assert/strict';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright-core';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const origin = new URL(process.env.T05_APP_URL ?? 'http://127.0.0.1:5173').origin;
assert.equal(new URL(origin).hostname, '127.0.0.1', 'Only the local synthetic review is allowed');
assert.equal(process.platform, 'win32', 'This gate requires real Windows Job Objects; no extraction replay');
const output = resolve(process.env.T05_BROWSER_OUT ?? resolve(root, '.local-review/t05-browser'));
mkdirSync(output, { recursive: true });
const pdf = resolve(output, 'synthetic-blood-gas.pdf');
const generator = spawnSync(process.env.CLINICAL_PYTHON ?? 'python', ['-c', `
from reportlab.pdfgen.canvas import Canvas
import sys
c=Canvas(sys.argv[1],pagesize=(420,340),invariant=1)
for lines in [
 ['Sample type: arterial blood','pH 7.30','pO2 80 mmHg','FiO2 40 %'],
 ['Muestra: arterial','pH 7.30','pO2 80 mmHg','FiO2 0.4 %']]:
 c.setFont('Helvetica',15)
 for i,line in enumerate(lines): c.drawString(18,310-i*30,line)
 c.showPage()
c.save()
`, pdf], { encoding: 'utf8' });
assert.equal(generator.status, 0, generator.stderr);
const executable = process.env.CHROMIUM_PATH ?? [
  resolve(process.env['ProgramFiles(x86)'] ?? 'C:/Program Files (x86)', 'Microsoft/Edge/Application/msedge.exe'),
  resolve(process.env.ProgramFiles ?? 'C:/Program Files', 'Google/Chrome/Application/chrome.exe'),
].find(existsSync);
assert.ok(executable, 'Provide the installed Chromium/Edge executable with CHROMIUM_PATH');
const browser = await chromium.launch({ executablePath: executable, headless: true });
const context = await browser.newContext({ viewport: { width: 1420, height: 1050 } });
const requests = [];
const errors = [];
context.on('request', (request) => requests.push({ method: request.method(), url: request.url() }));
const page = await context.newPage();
page.setDefaultTimeout(20_000);
page.on('pageerror', (error) => errors.push(error.message));
const checks = [];
let nominal;
try {
  const landing = await page.goto(origin);
  assert.equal(landing.status(), 200);
  assert.ok(landing.headers()['content-security-policy']?.includes("connect-src 'self'"));
  await page.locator('a[href="/blood-gas"]').click();
  await page.getByRole('heading', { name: 'Revisión de gasometrías', exact: true }).waitFor();
  const session = await page.evaluate(async () => (await fetch('/api/blood-gas/session', { cache: 'no-store' })).json());
  assert.equal(session.extraction_available, true);
  assert.equal(session.synthetic_only, true);
  assert.equal(await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length), 0);
  await page.getByLabel('Solo cargaré datos sintéticos', { exact: true }).check();
  const extraction = page.waitForResponse((response) => response.url().endsWith('/api/blood-gas/extract'), { timeout: 150_000 });
  await page.getByLabel('Documento sintético', { exact: true }).setInputFiles(pdf);
  const extractedResponse = await extraction;
  assert.equal(extractedResponse.status(), 200, 'The actual Windows extraction must succeed');
  const extracted = await extractedResponse.json();
  assert.equal(extracted.pages.length, 2);
  checks.push('real_windows_worker_upload_through_app_proxy');

  async function confirmFields() {
    for (const locator of await page.locator('[aria-label^="Transcripción manual de"]').all()) await locator.check();
    for (const locator of await page.locator('[aria-label^="Cotejo visual de"]').all()) await locator.check();
    for (const locator of await page.locator('select[aria-label^="Revisión de "]:not([aria-label*="metadato"])').all()) await locator.selectOption('confirmed');
    for (const label of ['He revisado el área completa', 'Todos los campos aceptados', 'Confirmo la revisión médica']) await page.getByLabel(label).check();
  }
  async function confirmMetadata() {
    for (const locator of await page.locator('[aria-label^="Ámbito de metadato"]').all()) await locator.selectOption('yes');
    for (const locator of await page.locator('[aria-label^="Revisión de metadato"]').all()) await locator.selectOption('confirmed');
  }
  const calculate = page.getByRole('button', { name: 'Interpretar valores confirmados', exact: true });
  await page.getByLabel('Tipo de muestra', { exact: true }).selectOption('arterial');
  await confirmMetadata();
  await confirmFields();
  assert.equal(await calculate.isEnabled(), true);
  let review = page.waitForResponse((response) => response.url().endsWith('/api/blood-gas/review'));
  await calculate.click();
  let reviewed = await review;
  assert.equal(reviewed.status(), 200);
  nominal = await reviewed.json();
  assert.equal(nominal.pao2_fio2_ratio_mm_hg, 200);
  assert.equal(nominal.fio2_trace.used_fraction, 0.4);
  checks.push('confirmed_percent_converted_once');

  await page.getByLabel('Página y muestra', { exact: true }).selectOption('1');
  assert.equal(await page.getByRole('region', { name: 'Resultado revisable' }).count(), 0);
  await page.getByLabel('Tipo de muestra', { exact: true }).selectOption('arterial');
  await confirmMetadata();
  await confirmFields();
  assert.equal(await calculate.isDisabled(), true);
  checks.push('invalid_percent_blocks_interpretation');
  await page.getByLabel('FiO2 unidad', { exact: true }).fill('fraction');
  await page.getByLabel('Motivo de la corrección de FiO₂', { exact: true }).fill('Unidad cotejada en escenario sintético');
  await confirmFields();
  review = page.waitForResponse((response) => response.url().endsWith('/api/blood-gas/review'));
  await calculate.click();
  reviewed = await review;
  assert.equal(reviewed.status(), 200);
  const corrected = await reviewed.json();
  assert.equal(corrected.pao2_fio2_ratio_mm_hg, 200);
  assert.equal(corrected.fio2_trace.used_fraction, 0.4);
  assert.equal(corrected.fio2_trace.corrected, true);
  checks.push('corrected_fraction_preserves_provenance');
  const raw = reviewed.request().postData();
  const duplicate = raw.replace('"medicalConfirmed":true', '"medicalConfirmed":false,"medicalConfirmed":true');
  assert.notEqual(duplicate, raw);
  const rejected = await context.request.post(origin + '/api/blood-gas/review', {
    data: duplicate, headers: { 'Content-Type': 'application/json', Origin: origin, 'X-Session': session.token },
  });
  assert.equal(rejected.status(), 422);
  checks.push('duplicate_clinical_confirmation_rejected_over_proxy');
  await page.getByLabel('FiO2 cifra', { exact: true }).fill('0.20');
  assert.equal(await page.getByRole('region', { name: 'Resultado revisable' }).count(), 0);
  assert.equal(await calculate.isDisabled(), true);
  checks.push('edited_out_of_range_fraction_clears_old_result');
  const revocation = page.waitForResponse((response) => response.url().endsWith('/api/blood-gas/reject'));
  await page.getByRole('button', { name: 'Rechazar y borrar la extracción', exact: true }).click();
  assert.equal((await revocation).status(), 200);
  await page.getByLabel('Página y muestra', { exact: true }).waitFor({ state: 'detached' });
  const staleReview = await context.request.post(origin + '/api/blood-gas/review', {
    data: raw, headers: { 'Content-Type': 'application/json', Origin: origin, 'X-Session': session.token },
  });
  assert.equal(staleReview.status(), 422);
  checks.push('reject_revokes_document');
  await page.screenshot({ path: resolve(output, 't05-composed-windows.png'), fullPage: true });
  assert.deepEqual(errors, []);
  assert.ok(requests.every((item) => new URL(item.url).origin === origin), 'Observed application requests must stay on its own origin');
  writeFileSync(resolve(output, 'RESULT.json'), JSON.stringify({
    status: 'PASS', platform: process.platform, browser: browser.version(), native_worker: true,
    origin, checks, requests, page_errors: errors, nominal_fio2_trace: nominal.fio2_trace,
    scope: 'Synthetic native Windows worker and real browser through the composed app; not OS-wide network capture or clinical validation',
  }, null, 2) + '\n');
  console.log(`PASS: ${checks.length} composed T05 Windows browser checks`);
} catch (error) {
  writeFileSync(resolve(output, 'RESULT.json'), JSON.stringify({ status: 'FAIL', checks, requests, page_errors: errors, error: String(error) }, null, 2) + '\n');
  await page.screenshot({ path: resolve(output, 't05-failure.png'), fullPage: true }).catch(() => {});
  throw error;
} finally {
  await context.close();
  await browser.close();
}
