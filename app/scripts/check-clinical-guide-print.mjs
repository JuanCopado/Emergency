// Run after npm run build. Uses an installed browser, and pypdf from
// clinical/requirements-test.txt via CLINICAL_QA_PYTHON (default: python).
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const guides = JSON.parse(await readFile(new URL('../src/data/generatedClinicalGuides.json', import.meta.url), 'utf8'));
const compact = (text) => text.replace(/\s+/g, '');
const server = await preview({ preview: { host: '127.0.0.1', port: 4173, strictPort: true }, logLevel: 'error' });
let browser;
try {
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  const page = await browser.newPage({ serviceWorkers: 'block' });
  for (const [path, id] of [
    ['/clinical/airway-rsi', 'airway-rsi'],
    ['/guides/airway-rsi', 'airway-rsi'],
    ['/guides/vf-pvt', 'adult-cardiac-arrest'],
    ['/guides/clinical-scores-calculators', 'clinical-scores-calculators'],
  ]) {
    const guide = guides.find((item) => item.id === id);
    await page.goto(`http://127.0.0.1:4173${path}`, { waitUntil: 'networkidle' });
    await page.locator('.canonical-body').waitFor();
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.canonical-body').evaluate((el) => el.ownerDocument.defaultView.getComputedStyle(el).visibility), 'visible');
    const pdf = await page.pdf({ preferCSSPageSize: true, printBackground: true });
    const extract = spawnSync(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-c',
      'import io,sys; from pypdf import PdfReader; sys.stdout.buffer.write("\\n".join(p.extract_text() for p in PdfReader(io.BytesIO(sys.stdin.buffer.read())).pages).encode("utf-8"))',
    ], { input: pdf, maxBuffer: 10 * 1024 * 1024 });
    assert.equal(extract.status, 0, extract.stderr?.toString());
    const text = compact(extract.stdout.toString('utf8'));
    for (const raw of [guide.sharedPreamble, guide.sectionBody].filter(Boolean).join('\n\n').split('\n')) {
      const line = raw.trim().replace(/^#{1,4} /, '').replace(/^- /, '');
      if (line) assert.ok(text.includes(compact(line)), `${path}: missing PDF text: ${line}`);
    }
    const sentinel = guide.sharedPreamble.split('\n').find((line) => line.startsWith('Shared gate:'));
    if (sentinel) assert.equal(text.split(compact(sentinel)).length - 1, 1, `${path}: duplicated safety preamble`);
    console.log(`PASS ${path}: canonical preamble and every body line extracted from browser PDF`);
  }
} finally {
  await browser?.close();
  await new Promise((resolve, reject) => server.httpServer.close((error) => error ? reject(error) : resolve()));
}
