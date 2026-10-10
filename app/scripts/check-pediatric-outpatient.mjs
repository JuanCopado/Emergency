// Production UI connected to the actual Python calculator, using loopback only.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
  'from http.server import ThreadingHTTPServer; from clinical_note_api import ClinicalNoteHandler; s=ThreadingHTTPServer(("127.0.0.1",0),ClinicalNoteHandler); print(s.server_port,flush=True); s.serve_forever()',
], { cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)), windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
let server, browser;
try {
  const port = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Pediatric API startup timeout')), 15000);
    let output = '';
    backend.stdout.on('data', (data) => {
      output += data.toString();
      if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); }
    });
    backend.on('error', (error) => { clearTimeout(timeout); reject(error); });
    backend.on('exit', (code) => { clearTimeout(timeout); reject(new Error(`API exited: ${code}`)); });
  });
  server = await preview({ preview: { host: '127.0.0.1', port: 4174, strictPort: true,
    proxy: { '/api/pediatric-outpatient': `http://127.0.0.1:${port}` } }, logLevel: 'error' });
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  const page = await browser.newPage({ serviceWorkers: 'block' });
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('http://127.0.0.1:4174/pediatrics');
  await page.getByRole('heading', { name: 'Pediatría ambulatoria' }).waitFor();
  assert.equal(await page.getByLabel('Diagnóstico y régimen').locator('option').count(), 90);
  assert.equal(await page.getByLabel('Fármaco o combinación').locator('option').count(), 53);
  const choose = (id) => page.getByLabel('Diagnóstico y régimen').selectOption(id);
  const calculate = () => page.getByRole('button', { name: 'Comprobar y calcular' }).click();
  const result = () => page.getByRole('region', { name: 'Resultado pediátrico' });
  await choose('paracetamol-pain-fever-home');
  await page.getByLabel('Edad (meses)', { exact: true }).fill('120');
  await page.getByLabel('Peso real (kg)', { exact: true }).fill('55');
  await page.getByLabel('Peso ideal (kg)', { exact: true }).fill('35');
  await page.getByLabel('Duración elegida', { exact: false }).fill('2');
  await calculate(); await result().waitFor();
  assert.match(await result().innerText(), /Cálculo bloqueado/);
  console.log('PASS real API: missing home gate blocks paracetamol');
  await page.getByLabel('home analgesia antipyresis appropriate', { exact: true }).selectOption('yes');
  await page.getByLabel('Concentración verificada (mg/mL)', { exact: true }).fill('24');
  await page.getByLabel('He verificado la concentración del producto exacto', { exact: true }).check();
  await calculate(); await result().waitFor();
  const text = await result().innerText();
  assert.match(text, /525/); assert.match(text, /21\.9/); assert.match(text, /175/);
  console.log('PASS real API: paracetamol ideal-weight dose and complete course');
  await choose('dexamethasone-croup-mild-moderate');
  await page.getByLabel('Edad (meses)', { exact: true }).fill('48');
  await page.getByLabel('Peso real (kg)', { exact: true }).fill('18');
  await page.getByLabel('croup discharge criteria met', { exact: true }).selectOption('yes');
  await page.getByLabel('Concentración verificada (mg/mL)', { exact: true }).fill('0.4');
  await page.getByLabel('He verificado la concentración del producto exacto', { exact: true }).check();
  await calculate(); await result().waitFor();
  assert.match(await result().innerText(), /6\.7[45]/);
  console.log('PASS real API: dexamethasone croup single-dose volume');
  await choose('rizatriptan-migraine-rch');
  await page.getByLabel('Edad (meses)', { exact: true }).fill('120');
  await page.getByLabel('Peso real (kg)', { exact: true }).fill('40');
  await page.getByLabel('secondary headache red flags excluded', { exact: true }).selectOption('yes');
  await calculate(); await page.getByRole('alert').filter({ hasText: 'no matching' }).waitFor();
  assert.equal(await result().count(), 0);
  console.log('PASS real API: unresolved 40 kg rizatriptan boundary remains blocked');
  assert.deepEqual(errors, []);
} finally {
  await browser?.close();
  if (server) await new Promise((resolve, reject) => server.httpServer.close((error) => error ? reject(error) : resolve()));
  backend.kill();
}
