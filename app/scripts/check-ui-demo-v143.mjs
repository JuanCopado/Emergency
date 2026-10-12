// DEMO-only end-to-end UI checks against the real loopback Python backend.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const root = new URL('../../clinical/qa/', import.meta.url);
const cases = JSON.parse(readFileSync(new URL('V1.43_DEMO_CASES.json', root), 'utf8')).cases;
assert.equal(cases.length, 15);
assert(cases.every(c => c.synthetic === true));
const backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
  'from http.server import ThreadingHTTPServer; from clinical_note_api import ClinicalNoteHandler; s=ThreadingHTTPServer(("127.0.0.1",0),ClinicalNoteHandler); print(s.server_port,flush=True); s.serve_forever()',
], { cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)), windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
let server, browser;
const report = { cases: [], exports: [], browser: '', errors: [] };
try {
  const port = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('API startup timeout')), 15000);
    let output = '';
    backend.stdout.on('data', data => { output += data.toString(); if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); } });
    backend.stderr.on('data', () => {});
    backend.on('error', error => { clearTimeout(timeout); reject(error); });
    backend.on('exit', code => { clearTimeout(timeout); reject(new Error(`API exited ${code}`)); });
  });
  server = await preview({ preview: { host: '127.0.0.1', port: 4176, strictPort: true, proxy: { '/api/clinical-note': `http://127.0.0.1:${port}` } }, logLevel: 'error' });
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  report.browser = browser.version();
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 }, serviceWorkers: 'block', acceptDownloads: true });
  await context.addInitScript(() => { localStorage.setItem('emergency.theme', 'light'); localStorage.setItem('emergency.lang', 'es'); });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(error.message));
  for (const c of cases) {
    await page.goto('http://127.0.0.1:4176' + c.route);
    await page.locator('main h1').waitFor();
    assert.doesNotMatch(await page.locator('main h1').innerText(), /no encontrado/);
    await page.goto('http://127.0.0.1:4176/clinical-note');
    await page.getByLabel('Idade', { exact: true }).fill(String(c.age_years));
    await page.getByLabel('Sexo', { exact: true }).selectOption(c.sex);
    await page.getByLabel('Motivo de consulta').fill(`DEMO sintético: ${c.presentation}`);
    await page.getByLabel('História da doença atual').fill(`DEMO. Peso referido ${c.weight_kg} kg. ${c.evolution}`);
    await page.getByLabel('Antecedentes · um por linha').fill(c.history);
    await page.getByLabel('Alergias · uma por linha').fill(c.allergies);
    await page.getByRole('button', { name: 'Exame', exact: true }).click();
    for (const [field, label] of [['bp','TA'],['hr','FC'],['rr','FR'],['spo2','SpO₂'],['temp','T °C']]) await page.getByLabel(label, { exact: true }).fill(String(c.vitals[field]));
    await page.getByRole('button', { name: 'Adicionar constantes', exact: true }).click();
    await page.getByRole('button', { name: 'MCDT', exact: true }).click();
    await page.getByLabel('Nome do exame').fill('DEMO - examen sintético');
    await page.getByLabel('Informe oficial / dados extraídos').fill(c.tests);
    await page.getByRole('button', { name: 'Criar cartão para revisão' }).click();
    await page.getByRole('button', { name: 'Exportar', exact: true }).click();
    assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
    await page.getByRole('button', { name: /^MCDT/ }).click();
    await page.getByTestId('mcdt-review-card').getByRole('button', { name: 'Aceitar', exact: true }).click();
    await page.getByRole('button', { name: 'Exportar', exact: true }).click();
    await page.getByLabel(/Identificadores diretos removidos/).check();
    await page.getByRole('button', { name: 'Apoio diagnóstico', exact: true }).click();
    const responsePromise = page.waitForResponse(r => r.url().endsWith('/api/clinical-note/analyze'));
    await page.getByRole('button', { name: 'Atualizar apoio diagnóstico' }).click();
    const response = await responsePromise;
    const body = await response.json();
    assert.equal(response.status(), 200, JSON.stringify(body));
    assert.equal(body.blocked, false, JSON.stringify(body));
    await page.getByText('Apoio atualizado', { exact: true }).waitFor();
    if (c.id === 'DEMO-01') await page.screenshot({ path: fileURLToPath(new URL('assets/v1.43/after/note-demo-analysis.webp', root)), type: 'webp', quality: 65 });
    await page.getByRole('button', { name: 'História', exact: true }).click();
    await page.getByLabel('História da doença atual').fill(`DEMO. Peso referido ${c.weight_kg} kg. ${c.evolution}. Reevaluación sintética añadida.`);
    await page.getByRole('button', { name: 'Apoio diagnóstico', exact: true }).click();
    await page.getByText(/Os dados mudaram/).waitFor();
    if (c.id === 'DEMO-01') {
      await page.getByRole('button', { name: 'Exportar', exact: true }).click();
      assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
      await page.getByLabel(/Médico reviu e valida/).check();
      for (const [label, extension] of [['JSON', '.json'], ['PDF', '.pdf'], ['Word (.docx)', '.docx']]) {
        const downloadPromise = page.waitForEvent('download');
        await page.getByRole('button', { name: label, exact: true }).click();
        const download = await downloadPromise;
        assert(download.suggestedFilename().endsWith(extension));
        assert.equal(await download.failure(), null);
        report.exports.push(extension);
      }
    }
    report.cases.push({ id: c.id, route: c.route, analysisHttp: response.status(), pendingBlocksExport: true, acceptedManualReport: true, staleAfterEdit: true });
    console.log(`PASS ${c.id}: route, entry, review, analysis, stale`);
  }
  assert.deepEqual(report.errors, []);
  await context.close();
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.httpServer.close(resolve));
  backend.kill();
  writeFileSync(new URL('assets/v1.43/after/demo-results.json', root), JSON.stringify(report, null, 2) + '\n');
}
