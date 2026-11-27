import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright-core';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';

const app = fileURLToPath(new URL('..', import.meta.url));
const dist = resolve(app, 'dist');
const compact = (value) => value.replace(/\s+/g, '');
const needle = 'BP below 160/100 mm Hg within the next 2 to 6 hours';
const warnings = [];
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
});
const result = {
  scope: 'CARDIO04 subsequent phase display and headless browser PDF text, two route families',
  transport: 'Real built artifact fulfillment on synthetic origin; no HTTP server/backend',
  browser: browser.version(),
  states: [],
  limitations: ['Not native operator printing, Word export, independent clinical validation or full browser regression.'],
};
try {
  const context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1366, height: 900 } });
  await context.route('**/*', async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== 'https://cardio04.test') return route.abort();
    const relative = decodeURIComponent(url.pathname).replace(/^\/+/, '');
    const path = extname(relative) ? resolve(dist, relative) : resolve(dist, 'index.html');
    assert.ok(path.startsWith(dist + sep));
    const type = { '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.html': 'text/html', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.png': 'image/png' }[extname(path)] || 'application/octet-stream';
    try { await route.fulfill({ status: 200, contentType: type, body: await readFile(path) }); }
    catch { await route.fulfill({ status: 404, body: '' }); }
  });
  for (const prefix of ['/clinical', '/guides']) {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto(`https://cardio04.test${prefix}/hypertensive-emergencies`, { waitUntil: 'networkidle' });
    const body = await page.locator('.canonical-body').innerText();
    for (const fragment of [needle, 'only if clinically stable', 'nonpregnant, nonstroke adults', 'SBP by no more than 25% within the first hour', 'aortic dissection, acute stroke, pulmonary edema, ACS or pre-eclampsia/eclampsia']) assert.ok(body.includes(fragment), `DOM missing ${fragment}`);
    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.canonical-body').evaluate((el) => el.ownerDocument.defaultView.getComputedStyle(el).visibility), 'visible');
    const pdf = await page.pdf({ preferCSSPageSize: true, printBackground: true });
    assert.ok(pdf.subarray(0, 5).toString() === '%PDF-');
    const loadingTask = getDocument({ data: new Uint8Array(pdf), disableFontFace: true, useSystemFonts: true });
    const document = await loadingTask.promise;
    let extracted = '';
    for (let n = 1; n <= document.numPages; n++) {
      const content = await (await document.getPage(n)).getTextContent();
      extracted += content.items.map((item) => item.str || '').join(' ') + '\n';
    }
    assert.ok(compact(extracted).includes(compact(needle)), 'PDF must retain strict below operator, unit and subsequent interval');
    assert.ok(compact(extracted).includes(compact('only if clinically stable')));
    assert.ok(compact(extracted).includes(compact('nonpregnant, nonstroke adults')));
    assert.equal(errors.length, 0, JSON.stringify(errors));
    result.states.push({ path: `${prefix}/hypertensive-emergencies`, dom: 'PASS', print_media: 'PASS', pdf_text: 'PASS', pdf_bytes: pdf.length, pdf_sha256: createHash('sha256').update(pdf).digest('hex'), pdf_pages: document.numPages, strict_operator_unit_interval_retained: true, errors });
    await loadingTask.destroy();
    await page.close();
  }
  await context.close();
  result.status = 'PASS';
  result.warnings = warnings;
  const output = resolve(app, '../docs/coordination/cardio04-stable-phase-20261127/BROWSER_PDF_QA.json');
  await writeFile(output, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result));
} finally { await browser.close(); }
