// Production UI + authenticated loopback proxy + real Python API; synthetic cases only.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';
import { clinicalTestSession } from './clinical-test-session.mjs';

const UI_PORT = 4187;
const appRoot = fileURLToPath(new URL('../', import.meta.url));
assert.ok(existsSync(join(appRoot, 'dist/index.html')), 'Run the current production build before this check');
const captures = process.env.UI_QA_SCREENSHOTS || fileURLToPath(new URL('../../docs/coordination/therapy-20261126/', import.meta.url));
mkdirSync(captures, { recursive: true });
const session = clinicalTestSession(UI_PORT);
const backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c', session.python], {
  cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)),
  env: session.environment, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'],
});
const baseUrl = `http://127.0.0.1:${UI_PORT}`;
const errors = [];
let server, browser;

async function noHorizontalOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({
    viewport: globalThis.window.innerWidth,
    document: globalThis.document.documentElement.scrollWidth,
    body: globalThis.document.body.scrollWidth,
  }));
  assert.ok(dimensions.document <= dimensions.viewport + 1 && dimensions.body <= dimensions.viewport + 1,
    `${label}: horizontal overflow ${JSON.stringify(dimensions)}`);
}

async function captureAtWidths(page, anchor, name) {
  for (const width of [1366, 360]) {
    await page.setViewportSize({ width, height: width === 360 ? 800 : 900 });
    await anchor.evaluate(element => element.scrollIntoView({ block: 'center' }));
    await noHorizontalOverflow(page, `${name} ${width}px`);
    await page.screenshot({ path: join(captures, `${name}-${width}.webp`), type: 'webp', quality: 78 });
  }
  await page.setViewportSize({ width: 1366, height: 900 });
}

async function realApi(page, endpoint, action) {
  const incoming = page.waitForResponse(response => response.url().endsWith(endpoint) && response.request().method() === 'POST');
  await action();
  const response = await incoming;
  assert.equal(response.status(), 200, `${endpoint}: HTTP ${response.status()}`);
  const data = await response.json();
  assert.equal(data.blocked, false, `${endpoint}: ${JSON.stringify(data.issues || data.findings || data)}`);
  return { data, request: response.request().postDataJSON() };
}

async function newPage() {
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 }, serviceWorkers: 'block' });
  page.setDefaultTimeout(15000);
  await page.addInitScript(() => localStorage.setItem('emergency.lang', 'es'));
  page.on('pageerror', error => errors.push(error.message));
  return page;
}

const syntheticSections = {
  'Actuaciones iniciales': 'Caso sintético de QA: medidas individualizadas de prueba, sin intervención clínica real.',
  'Medicación y pauta completa': 'Caso sintético de QA: no se indica medicación; no representa una prescripción.',
  'Monitorización': 'Caso sintético de QA: observación de prueba documentada, sin paciente real.',
  'Reevaluación': 'Caso sintético de QA: reevaluación de prueba y escalada documentadas.',
  'Destino y seguimiento': 'Caso sintético de QA: destino de prueba documentado, sin paciente real.',
};

async function fillSyntheticPlan(page) {
  await page.getByRole('button', { name: 'Editar pauta', exact: true }).click();
  for (const [label, value] of Object.entries(syntheticSections)) {
    await page.getByLabel(label, { exact: true }).fill(value);
  }
}

async function confirmAndReview(page) {
  await page.getByLabel('He revisado el caso actual y la pauta completa', { exact: false }).check();
  await page.getByLabel('He aplicado la seguridad farmacológica central', { exact: false }).check();
  const response = await realApi(page, '/api/clinical-note/therapy/validate', () => page.getByRole('button', { name: 'Validar pauta', exact: true }).click());
  assert.equal(response.data.review.scope, 'physician_review_of_this_version');
  await page.getByRole('button', { name: 'Pauta validada', exact: true }).waitFor();
  assert.match(await page.getByTestId('therapy-review-state').innerText(), /Revisión médica vigente/);
  const color = await page.getByRole('button', { name: 'Pauta validada', exact: true }).evaluate(element => globalThis.getComputedStyle(element).backgroundColor);
  const rgb = color.match(/\d+/g)?.map(Number);
  assert.ok(rgb && rgb[1] > rgb[0], `Validated button is not green: ${color}`);
  return response.data.review;
}

async function prepareCase(page, { age, unit, weight, moduleId, label }) {
  await page.goto(`${baseUrl}/clinical-note`);
  await page.getByTestId('clinical-note-workspace').waitFor();
  await page.getByLabel('Unidad de edad', { exact: true }).selectOption(unit);
  await page.getByLabel('Edad', { exact: true }).fill(age);
  await page.getByLabel('Motivo de consulta', { exact: true }).fill('Evaluación sintética de QA sin paciente real.');
  await page.getByTestId('note-tab-plan').click();
  await page.getByLabel('Diagnóstico o patología', { exact: true }).fill(label);
  await page.getByLabel('Referencia clínica', { exact: true }).locator(`option[value="${moduleId}"]`).waitFor({ state: 'attached' });
  await page.getByLabel('Referencia clínica', { exact: true }).selectOption(moduleId);
  await page.getByLabel('Peso (kg)', { exact: true }).fill(weight);
  await page.getByLabel('He revisado las alergias de este caso', { exact: true }).check();
  await page.getByLabel('He retirado identificadores y revisado la privacidad del texto y de los archivos', { exact: true }).check();
  return realApi(page, '/api/clinical-note/therapy/suggest', () => page.getByRole('button', { name: 'Preparar pauta', exact: true }).click());
}

try {
  const port = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Therapeutic API startup timeout')), 15000);
    let output = '';
    backend.stdout.on('data', data => {
      output += data.toString();
      if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); }
    });
    backend.on('error', error => { clearTimeout(timeout); reject(error); });
    backend.on('exit', code => { clearTimeout(timeout); reject(new Error(`Therapeutic API exited: ${code}`)); });
  });
  server = await preview({ root: appRoot, preview: {
    host: '127.0.0.1', port: UI_PORT, strictPort: true,
    proxy: { '/api/clinical-note': session.proxy(port) },
  }, logLevel: 'error' });
  const executablePath = process.env.CHROMIUM_PATH || (existsSync(chromium.executablePath()) ? chromium.executablePath() : chromiumPath());
  browser = await chromium.launch({ executablePath, headless: true });

  const comparator = await newPage();
  await comparator.goto(`${baseUrl}/corticosteroids`);
  await comparator.getByRole('heading', { name: 'Corticoides', level: 1 }).waitFor();
  await comparator.getByLabel('Referencia de equivalencia', { exact: true }).selectOption('endotext-2018');
  await comparator.getByLabel('Cantidad en mg', { exact: true }).fill('20');
  await comparator.getByLabel('Vía sistémica de la comparación', { exact: true }).selectOption('iv');
  await comparator.getByLabel('Qué cantidad estás comparando', { exact: true }).selectOption('daily_total');
  await comparator.getByRole('button', { name: 'Comparar', exact: true }).click();
  const result = comparator.getByRole('region', { name: 'Equivalencias aproximadas', exact: true });
  await result.waitFor();
  assert.equal(await result.locator('tbody tr').count(), 8);
  assert.match(await result.innerText(), /Endotext 2018/);
  assert.equal(await result.getByRole('row').filter({ hasText: 'Dexametasona' }).getByRole('cell').first().innerText(), '0,75');
  assert.match(await comparator.getByRole('region', { name: 'Adultos', exact: true }).innerText(), /50 mg IV\/IM cada 6 h/);
  assert.match(await comparator.getByRole('region', { name: 'Pediatría · Crisis suprarrenal', exact: true }).innerText(), /No trasladar al niño/);
  await captureAtWidths(comparator, result, 'corticosteroid-comparison');
  await comparator.getByLabel('Cantidad en mg', { exact: true }).fill('21');
  assert.equal(await result.count(), 0, 'Editing a comparison input must remove stale equivalents');
  console.log('PASS corticosteroids: Endotext 20 mg, eight results, adult/pediatric separation, edit invalidation, desktop/360px');

  const adult = await newPage();
  const suggested = await prepareCase(adult, { age: '55', unit: 'years', weight: '70', moduleId: 'acute-severe-asthma', label: 'Caso sintético adulto de QA' });
  assert.deepEqual(suggested.request.note.encounter.age, { years: 55, months: null });
  assert.equal(suggested.data.plan.population, 'adult');
  assert.equal(suggested.data.plan.medication_safety.actionable, false);
  await fillSyntheticPlan(adult);
  const redButton = adult.getByRole('button', { name: 'Validar pauta', exact: true });
  const red = await redButton.evaluate(element => globalThis.getComputedStyle(element).backgroundColor);
  const redRgb = red.match(/\d+/g)?.map(Number);
  assert.ok(redRgb && redRgb[0] > redRgb[1], `Unreviewed button is not red: ${red}`);
  await captureAtWidths(adult, redButton, 'therapy-unreviewed');
  const firstReceipt = await confirmAndReview(adult);
  await captureAtWidths(adult, adult.getByRole('button', { name: 'Pauta validada', exact: true }), 'therapy-reviewed');
  await adult.getByTestId('note-tab-export').click();
  const exportButton = adult.getByRole('button', { name: 'JSON', exact: true });
  assert.equal(await exportButton.isEnabled(), true, 'A reviewed current plan must enable export');
  const exportResponse = adult.waitForResponse(response => response.url().endsWith('/api/clinical-note/export'));
  const downloadEvent = adult.waitForEvent('download');
  await exportButton.click();
  const exportedResponse = await exportResponse;
  assert.equal(exportedResponse.status(), 200);
  const downloaded = await downloadEvent;
  assert.equal(downloaded.suggestedFilename(), 'clinical-note.json');
  const envelope = await exportedResponse.json();
  const exported = JSON.parse(Buffer.from(envelope.content_base64, 'base64').toString('utf8'));
  assert.equal(exported.therapeutic_review.plan_digest, firstReceipt.plan_digest);
  assert.equal(exported.therapeutic_plan.medication_safety.actionable, false);
  assert.deepEqual(exported.assessment.treatment_suggestions, []);
  assert.deepEqual(exported.assessment.disposition, []);
  assert.deepEqual(exported.assessment.reassessment, []);
  assert.equal(exported.therapeutic_plan.sections.medications, syntheticSections['Medicación y pauta completa']);

  await adult.getByTestId('note-tab-plan').click();
  await adult.getByRole('button', { name: 'Editar pauta', exact: true }).click();
  await adult.getByLabel('Destino y seguimiento', { exact: true }).fill(`${syntheticSections['Destino y seguimiento']} Edición sintética posterior.`);
  assert.match(await adult.getByTestId('therapy-review-state').innerText(), /Pendiente de validación médica/);
  await adult.getByTestId('note-tab-export').click();
  assert.equal(await adult.getByRole('button', { name: 'JSON', exact: true }).isDisabled(), true, 'Editing the plan must block export');
  await adult.getByTestId('note-tab-plan').click();
  const secondReceipt = await confirmAndReview(adult);
  assert.notEqual(secondReceipt.plan_digest, firstReceipt.plan_digest);
  console.log('PASS adult real API: red → green, actual JSON download, edit → red/export blocked, re-review → green');

  const child = await newPage();
  const pediatric = await prepareCase(child, { age: '8', unit: 'months', weight: '8', moduleId: 'bronchiolitis', label: 'Caso sintético pediátrico de QA' });
  assert.deepEqual(pediatric.request.note.encounter.age, { years: null, months: 8 });
  assert.equal(pediatric.data.plan.population, 'pediatric');
  assert.deepEqual(pediatric.data.plan.source_refs.map(source => source.module_id), ['bronchiolitis']);
  assert.equal(pediatric.data.plan.medication_safety.actionable, false);
  assert.doesNotMatch(pediatric.data.plan.sections.medications, /200\s*mg/);
  assert.doesNotMatch(pediatric.data.plan.reference_text, /## acute-severe-asthma/);
  await fillSyntheticPlan(child);
  await confirmAndReview(child);
  for (const width of [1366, 360]) {
    await child.setViewportSize({ width, height: 800 });
    await noHorizontalOverflow(child, `pediatric note ${width}px`);
  }
  console.log('PASS pediatric real API: eight months exclusive, pediatric-only source, no adult dose conversion, physician review, desktop/360px');
  assert.deepEqual(errors, [], `Browser page errors: ${errors.join('; ')}`);
  console.log('PASS no pageerrors; screenshots contain only synthetic cases');
} finally {
  await browser?.close();
  if (server) await new Promise((resolve, reject) => server.httpServer.close(error => error ? reject(error) : resolve()));
  backend.kill();
}
