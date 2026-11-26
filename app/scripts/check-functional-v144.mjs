// Synthetic input -> real API -> visible UI -> JSON export; no clinical accuracy claim.
import assert from 'node:assert/strict';
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';
import { clinicalTestSession } from './clinical-test-session.mjs';

const qa = new URL('../../clinical/qa/', import.meta.url);
const labels = JSON.parse(readFileSync(new URL('../src/i18n/locales/es.clinical.json', import.meta.url), 'utf8'));
function ui(key) {
  if (key.startsWith('+ ')) return `+ ${ui(key.slice(2))}`;
  if (['SpO₂', 'GCS'].includes(key)) return key;
  assert.equal(typeof labels[key], 'string', `Missing Spanish selector: ${key}`);
  return labels[key];
}
const pilot = process.argv.includes('--pilot');
const bank = JSON.parse(readFileSync(new URL('V1.44_DEMO_CASES.json', qa), 'utf8'));
const cases = bank.cases.filter(c => c.layer === 'note' && (!pilot || c.pilot));
const report = { scope: pilot ? 'pilot-note-browser' : 'note-browser', base_sha: bank.base_sha, cases: [], errors: [] };
const repoRoot = fileURLToPath(new URL('../../', import.meta.url));
report.provenance = {
  head_sha: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: repoRoot, encoding: 'utf8' }).trim(),
  dirty: !!execFileSync('git', ['status', '--porcelain'], { cwd: repoRoot, encoding: 'utf8' }).trim(),
  sha256: Object.fromEntries(['app/scripts/check-functional-v144.mjs', 'app/src/clinical-note/api.ts', 'clinical/scripts/clinical_note_api.py']
    .map(path => [path, createHash('sha256').update(readFileSync(join(repoRoot, path))).digest('hex')])),
};
const session = clinicalTestSession(4177);
const backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
  session.python,
], { cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)), env: session.environment, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
let server, browser;
try {
  const port = await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('API startup timeout')), 15000);
    let output = '';
    backend.stdout.on('data', data => { output += data; if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); } });
    backend.stderr.on('data', () => {});
    backend.on('error', error => { clearTimeout(timeout); reject(error); });
    backend.on('exit', code => { clearTimeout(timeout); reject(new Error(`API exited ${code}`)); });
  });
  server = await preview({ preview: { host: '127.0.0.1', port: 4177, strictPort: true, proxy: { '/api/clinical-note': session.proxy(port) } }, logLevel: 'error' });
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  report.browser = browser.version();
  const context = await browser.newContext({ serviceWorkers: 'block', acceptDownloads: true });
  await context.addInitScript(() => { localStorage.setItem('emergency.lang', 'es'); });
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.on('pageerror', error => report.errors.push(error.message));
  for (const entry of cases) {
    const c = entry.input;
    const row = { id: entry.id };
    try {
      await page.goto('http://127.0.0.1:4177/clinical-note');
      await page.getByLabel(ui('Idade'), { exact: true }).fill(String(c.age_years));
      await page.getByLabel(ui('Sexo'), { exact: true }).selectOption(c.sex || 'unknown');
      await page.getByLabel(ui('Motivo de consulta')).fill(c.chief_complaint);
      await page.getByLabel(ui('História da doença atual')).fill(c.hpi || '');
      await page.getByRole('button', { name: ui('Exame'), exact: true }).click();
      await page.getByLabel(ui('Exploração'), { exact: true }).fill(['exam_respiratory', 'exam_neurologic', 'exam_cardiovascular'].map(k => c[k]).filter(Boolean).join('\n'));
      if (c.vitals) {
        for (const [key, label] of [['bp','TA'],['hr','FC'],['rr','FR'],['spo2','SpO₂'],['temperature_c','T °C'],['oxygen','O₂ / dispositivo'],['gcs','GCS']]) {
          if (c.vitals[key] != null) await page.getByLabel(ui(label), { exact: true }).fill(String(c.vitals[key]));
        }
        await page.getByRole('button', { name: ui('Adicionar constantes'), exact: true }).click();
      }
      const exams = [['ecg', '+ ECG'], ['labs', '+ Analítica'], ['blood_gas', '+ Gasometria']].filter(([key]) => c[key]);
      // An inert synthetic manual report exercises acceptance even without a clinical test fixture.
      if (!exams.length) exams.push(['demo', '+ Outro']);
      for (const [key, button] of exams) {
        await page.getByRole('button', { name: new RegExp(`^${ui('MCDT')}`) }).click();
        await page.getByRole('button', { name: ui(button), exact: true }).click();
        await page.getByLabel(ui('Nome do exame')).fill(`DEMO ${key}`);
        await page.getByLabel(ui('Informe oficial / dados extraídos')).fill(c[key] || 'DEMO sintético; sem exame adicional.');
        await page.getByRole('button', { name: ui('Criar cartão para revisão') }).click();
        await page.getByRole('button', { name: 'Exportar', exact: true }).click();
        assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
        await page.getByRole('button', { name: new RegExp(`^${ui('MCDT')}`) }).click();
        await page.getByTestId('mcdt-review-card').last().getByRole('button', { name: ui('Aceitar'), exact: true }).click();
      }
      await page.getByRole('button', { name: 'Exportar', exact: true }).click();
      await page.getByLabel(ui('Identificadores diretos removidos; texto livre, metadados e privacidade revistos.'), { exact: true }).check();
      await page.getByRole('button', { name: ui('Apoio diagnóstico'), exact: true }).click();
      const responsePromise = page.waitForResponse(r => r.url().endsWith('/api/clinical-note/analyze'));
      await page.getByRole('button', { name: ui('Atualizar apoio diagnóstico') }).click();
      const response = await responsePromise;
      const body = await response.json();
      assert.equal(response.status(), 200);
      assert.equal(body.blocked, false);
      const input = response.request().postDataJSON().note;
      assert.equal(input.history.chief_complaint, c.chief_complaint);
      assert.equal(input.encounter.age.years, c.age_years);
      const a = body.assessment;
      assert(a.likely_diagnoses.some(d => d.diagnosis === c.expected_likely), `expected ${c.expected_likely}; got ${a.likely_diagnoses.map(d => d.diagnosis)}`);
      const modules = new Set(a.likely_diagnoses.flatMap(d => d.source_modules));
      for (const m of c.expected_modules || []) assert(modules.has(m), `missing ${m}`);
      for (const d of c.expected_must_not_miss || []) assert(a.must_not_miss.some(x => x.diagnosis === d), `missing ${d}`);
      if (c.expected_test_contains) assert(a.suggested_tests.some(x => x.action.toLowerCase().includes(c.expected_test_contains.toLowerCase())));
      if (c.expected_immediate_treatment_module) assert(a.treatment_suggestions.some(x => x.source_modules.includes(c.expected_immediate_treatment_module)));
      await page.getByText(ui('Apoio atualizado'), { exact: true }).waitFor();
      const visible = await page.locator('main').innerText();
      for (const d of [...a.likely_diagnoses, ...a.must_not_miss]) assert(visible.includes(d.diagnosis), `UI omitted ${d.diagnosis}`);
      await page.getByRole('button', { name: ui('Plano'), exact: true }).click();
      const plan = await page.locator('main').innerText();
      for (const suggestion of [...a.suggested_tests, ...a.treatment_suggestions]) assert(plan.includes(suggestion.action), 'UI omitted action');
      await page.getByRole('button', { name: 'Exportar', exact: true }).click();
      assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
      await page.getByLabel(ui('Médico reviu e valida o conteúdo clínico atual.'), { exact: true }).check();
      const exportPromise = page.waitForResponse(r => r.url().endsWith('/api/clinical-note/export'));
      const downloadPromise = page.waitForEvent('download');
      await page.getByRole('button', { name: 'JSON', exact: true }).click();
      const exportResponse = await exportPromise;
      assert.equal(exportResponse.status(), 200);
      const download = await downloadPromise;
      assert.equal(await download.failure(), null);
      const exported = JSON.parse(readFileSync(await download.path(), 'utf8'));
      const submitted = exportResponse.request().postDataJSON().note;
      assert.deepEqual(exported, submitted, 'download differs from UI submitted note');
      assert.deepEqual(exported.assessment, a, 'export differs from analysis');
      if (c.id === 'acs-st-elevation') {
        row.binary_downloads = [];
        for (const [label, format] of [['PDF', 'pdf'], ['Word (.docx)', 'docx']]) {
          const binaryPromise = page.waitForEvent('download');
          await page.getByRole('button', { name: label, exact: true }).click();
          const binary = await binaryPromise;
          assert.equal(await binary.failure(), null);
          if (process.env.FUNCTIONAL_QA_DOWNLOAD_DIR) {
            mkdirSync(process.env.FUNCTIONAL_QA_DOWNLOAD_DIR, { recursive: true });
            await binary.saveAs(join(process.env.FUNCTIONAL_QA_DOWNLOAD_DIR, `synthetic-acs.${format}`));
          }
          const verifier = spawnSync(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-c',
            'import sys,zipfile; from xml.etree import ElementTree; from pypdf import PdfReader; p,fmt,expected=sys.argv[1:]; text="\\n".join(x.extract_text() for x in PdfReader(p).pages) if fmt=="pdf" else "".join(ElementTree.fromstring(zipfile.ZipFile(p).read("word/document.xml")).itertext()); assert expected in text; assert "Validación médica" in text',
            await binary.path(), format, c.expected_likely,
          ], { windowsHide: true, encoding: 'utf8', timeout: 15000 });
          assert.equal(verifier.status, 0, verifier.stderr || verifier.error?.message);
          row.binary_downloads.push({ format, diagnosis_and_review_text: 'PASS' });
        }
      }
      await page.getByRole('button', { name: ui('História'), exact: true }).click();
      await page.getByLabel(ui('História da doença atual')).fill(`${c.hpi || ''}\nDEMO: reavaliação pendente.`);
      await page.getByRole('button', { name: ui('Apoio diagnóstico'), exact: true }).click();
      await page.getByText(ui('Os dados mudaram desde a última análise; resultado marcado como desatualizado.')).waitFor();
      await page.getByRole('button', { name: 'Exportar', exact: true }).click();
      assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
      Object.assign(row, { status: 'PASS', input_api_ui: 'PASS', expected_output: 'PASS', actions_visible: 'PASS', json_download_exact: 'PASS', pending_review_stale_gates: 'PASS' });
    } catch (error) {
      Object.assign(row, { status: 'FAIL', error: error.message });
    }
    report.cases.push(row);
    console.log(`${row.status} ${row.id}${row.error ? ': ' + row.error : ''}`);
  }
  assert.deepEqual(report.errors, []);
  assert(report.cases.every(c => c.status === 'PASS'), 'functional browser failures; inspect report');
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.httpServer.close(resolve));
  backend.kill();
  writeFileSync(process.env.FUNCTIONAL_QA_OUTPUT ?? new URL(pilot ? 'V1.44_BROWSER_PILOT_RESULTS.json' : 'V1.44_BROWSER_RESULTS.json', qa), JSON.stringify(report, null, 2) + '\n');
}
