// Missing integration coverage only: real loopback HTTP/API, synthetic non-prescribing input.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { withClinicalApp } from './functional-harness.mjs';

const output = process.env.MINIMAL_HTTP_QA_OUTPUT;
assert(output, 'MINIMAL_HTTP_QA_OUTPUT must name an evidence directory');
if (process.env.MINIMAL_HTTP_REQUIRE_WINDOWS === '1') assert.equal(process.platform, 'win32', 'Windows evidence requires a real Windows process');
if (process.platform === 'win32' && !process.env.CHROMIUM_PATH) {
  process.env.CHROMIUM_PATH = process.env.CHROME_PATH || [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  ].find(existsSync);
}
const destination = resolve(output);
mkdirSync(destination, { recursive: true });
const intro = JSON.parse(readFileSync(new URL('../src/pages/clinical-minimal-copy.json', import.meta.url), 'utf8'));
const therapy = JSON.parse(readFileSync(new URL('../src/clinical-note/therapyCopy.locales.json', import.meta.url), 'utf8'));
const report = {
  scope: 'Previously unverified Clinical Minimal integration; no clinical validity or native printing certification',
  platform: process.platform, architecture: process.arch, transport: 'REAL_LOOPBACK_HTTP_WITH_AUTHENTICATED_PYTHON_API',
  browserControl: 'playwright-core/preinstalled browser',
  responseInterception: false, sourceRevision: process.env.MINIMAL_HTTP_SOURCE_SHA || null,
  harnessSha256: createHash('sha256').update(readFileSync(fileURLToPath(import.meta.url))).digest('hex'),
  status: 'RUNNING', complementaryHeroStates: [], navigation: [], clinicalFlows: [], apiResponses: [], errors: [],
  limits: ['No screen reader or native Word/PDF application/print dialog operated by this script',
    'Blood gas and T06 entry navigation does not certify their separate native services'],
};
const sourceRoot = fileURLToPath(new URL('../', import.meta.url));
assert(existsSync(join(sourceRoot, 'dist/index.html')), 'Build the requested source before HTTP validation');

async function noOverflow(page) {
  assert(await page.evaluate(() => globalThis.document.documentElement.scrollWidth <= globalThis.innerWidth + 1), 'Horizontal overflow');
}

async function apiAction(page, endpoint, action) {
  const incoming = page.waitForResponse(r => r.url().endsWith(endpoint) && r.request().method() === 'POST');
  await action();
  const response = await incoming;
  assert.equal(response.status(), 200, `${endpoint}: HTTP ${response.status()}`);
  const data = await response.json();
  if (endpoint.endsWith('/export')) {
    assert.equal(typeof data.content_base64, 'string', 'Missing export content');
    assert.equal(typeof data.filename, 'string', 'Missing export filename');
  } else assert.equal(data.blocked, false, `${endpoint}: operation blocked`);
  return { data, response };
}

async function enterFromHome(page, base, path) {
  await page.goto(`${base}/?design=clinical-minimal`);
  await page.locator('.clinical-minimal-scene img').waitFor();
  const anchor = page.locator(`a[href="${path}"]:visible`).first();
  await anchor.click();
  await page.waitForURL(`${base}${path}`);
  await page.locator('.clinical-minimal-preview').waitFor({ state: 'detached' });
  await page.locator('main h1').waitFor();
  assert.equal(await page.locator('main').getAttribute('id'), 'main');
  await noOverflow(page);
}

async function downloadExport(page, format, marker) {
  const pendingDownload = page.waitForEvent('download');
  const exported = await apiAction(page, '/api/clinical-note/export', () => page.getByRole('button', { name: format === 'Word' ? 'Word (.docx)' : format, exact: true }).click());
  const download = await pendingDownload;
  assert.equal(await download.failure(), null);
  const path = join(destination, `${marker}-${basename(download.suggestedFilename())}`);
  await download.saveAs(path);
  const bytes = readFileSync(path);
  if (format === 'JSON') {
    const note = JSON.parse(bytes.toString('utf8'));
    assert.equal(note.therapeutic_plan.medication_safety.actionable, false);
    assert(note.therapeutic_review.plan_digest);
    assert(note.therapeutic_plan.sections.medications.includes('SYNTHETIC NON-PRESCRIBING QA'));
  } else if (format === 'PDF') assert.equal(bytes.subarray(0, 5).toString('ascii'), '%PDF-');
  else assert.equal(bytes.subarray(0, 2).toString('ascii'), 'PK');
  return { format, filename: basename(path), bytes: bytes.length, httpStatus: exported.response.status() };
}

async function clinicalFlow(page, base, lang) {
  const labels = JSON.parse(readFileSync(new URL(`../src/i18n/locales/${lang}.clinical.json`, import.meta.url), 'utf8'));
  const ui = key => labels[key] || key;
  const copy = therapy[lang];
  await enterFromHome(page, base, '/clinical-note');
  await page.getByTestId('clinical-note-workspace').waitFor();
  await page.getByRole('combobox', { name: copy.ageUnit, exact: true }).selectOption('years');
  await page.getByLabel(ui('Idade'), { exact: true }).fill('55');
  await page.getByLabel(ui('Motivo de consulta'), { exact: true }).fill('SYNTHETIC NON-PRESCRIBING QA; no real patient.');
  await page.getByTestId('note-tab-plan').click();
  await page.getByRole('textbox', { name: copy.diagnosis, exact: true }).fill('Synthetic QA scenario');
  await page.getByRole('combobox', { name: copy.module, exact: true }).selectOption('acute-severe-asthma');
  await page.getByRole('textbox', { name: copy.weight, exact: true }).fill('70');
  await page.getByLabel(copy.allergies, { exact: true }).check();
  await page.getByLabel(copy.privacy, { exact: true }).check();
  const generated = await apiAction(page, '/api/clinical-note/therapy/suggest', () => page.getByRole('button', { name: copy.suggest, exact: true }).click());
  assert.equal(generated.data.plan.medication_safety.actionable, false);
  await page.getByTestId('note-tab-export').click();
  for (const name of ['JSON', 'PDF', 'Word']) assert(await page.getByRole('button', { name: name === 'Word' ? 'Word (.docx)' : name, exact: true }).isDisabled(), `Unreviewed ${name} export enabled`);
  await page.getByTestId('note-tab-plan').click();
  await page.getByRole('button', { name: copy.edit, exact: true }).click();
  for (const key of ['initial_actions', 'medications', 'monitoring', 'reassessment', 'disposition']) {
    await page.getByRole('textbox', { name: copy[key], exact: true }).fill(`SYNTHETIC NON-PRESCRIBING QA ${key}; no treatment or real patient.`);
  }
  await page.getByLabel(copy.individualized, { exact: true }).check();
  assert(await page.getByRole('button', { name: copy.validate, exact: true }).isDisabled(), 'Missing safety confirmation must block review');
  await page.getByLabel(copy.safety, { exact: true }).check();
  const reviewed = await apiAction(page, '/api/clinical-note/therapy/validate', () => page.getByRole('button', { name: copy.validate, exact: true }).click());
  assert.equal(reviewed.data.review.scope, 'physician_review_of_this_version');
  await page.getByRole('button', { name: copy.validated, exact: true }).waitFor();
  await page.getByTestId('note-tab-export').click();
  const exports = [await downloadExport(page, 'JSON', lang)];
  if (lang === 'pt') exports.push(await downloadExport(page, 'PDF', lang));
  if (lang === 'zh') exports.push(await downloadExport(page, 'Word', lang));
  await page.getByTestId('note-tab-plan').click();
  await page.getByRole('button', { name: copy.edit, exact: true }).click();
  await page.getByRole('textbox', { name: copy.disposition, exact: true }).fill('SYNTHETIC NON-PRESCRIBING QA edited after review.');
  await page.getByTestId('note-tab-export').click();
  for (const name of ['JSON', 'PDF', 'Word']) assert(await page.getByRole('button', { name: name === 'Word' ? 'Word (.docx)' : name, exact: true }).isDisabled(), `Edited ${name} export enabled`);
  await noOverflow(page);
  return { lang, entry: 'Visible opt-in Home -> actual navigation -> clinical note', realSuggest: true, realVersionReview: true,
    unreviewedAndEditedExportsBlocked: true, missingSafetyConfirmationBlocked: true, exports };
}

try {
  await withClinicalApp(async ({ browser, base }) => {
    report.browser = browser.version();
    report.origin = base;
    for (const [lang, theme] of [['es', 'dark'], ['pt', 'light'], ['en', 'dark'], ['zh', 'light']]) {
      const context = await browser.newContext({ viewport: { width: 1366, height: 900 }, serviceWorkers: 'block', acceptDownloads: true });
      await context.addInitScript(({ lang, theme }) => {
        globalThis.localStorage.setItem('emergency.lang', lang);
        globalThis.localStorage.setItem('emergency.theme', theme);
      }, { lang, theme });
      const page = await context.newPage();
      page.setDefaultTimeout(15000);
      page.on('pageerror', error => report.errors.push(error.message));
      page.on('response', response => {
        const url = new URL(response.url());
        if (url.pathname.startsWith('/api/clinical-note')) report.apiResponses.push({ endpoint: url.pathname, status: response.status() });
      });
      for (const width of [360, 1366]) {
        await page.setViewportSize({ width, height: 900 });
        await page.goto(`${base}/?design=clinical-minimal`);
        await page.locator('.clinical-minimal-scene img').waitFor();
        const buildRevision = await page.getByTestId('build-identity').locator('code').first().getAttribute('title');
        if (report.sourceRevision) assert.equal(buildRevision, report.sourceRevision, 'Served build revision differs from requested source');
        report.servedBuildRevision = buildRevision;
        const heading = page.locator('main h1');
        assert.equal(await heading.count(), 1);
        assert.equal((await heading.innerText()).replace(/\s/g, ''), intro[lang].title.replaceAll('<br>', '').replace(/\s/g, ''));
        assert.equal(await page.locator('.clinical-minimal-scene img').getAttribute('alt'), intro[lang].doctorDesc);
        assert(await page.locator('.clinical-minimal-scene img').evaluate(image => image.complete && image.naturalWidth > 0));
        await noOverflow(page);
        await page.getByRole('searchbox').focus();
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => globalThis.getComputedStyle(globalThis.document.activeElement).outlineWidth), '3px');
        await page.screenshot({ path: join(destination, `complementary-${lang}-${theme}-${width}.png`), fullPage: true });
        report.complementaryHeroStates.push({ lang, theme, width, heading: 'PASS', illustration: 'loaded', focus: 'visible', overflow: false });
      }
      const hrefs = await page.locator('main a').evaluateAll(anchors => anchors.map(anchor => anchor.getAttribute('href')));
      assert.equal(hrefs.length, 30);
      for (const [index, href] of hrefs.entries()) {
        await page.goto(`${base}/?design=clinical-minimal`);
        await page.locator('main a').nth(index).click();
        await page.waitForURL(new URL(href, base).href);
        await page.locator('.clinical-minimal-preview').waitFor({ state: 'detached' });
        await page.locator('main h1').waitFor();
        assert.equal(await page.locator('.clinical-minimal-preview').count(), 0, 'Opt-in styles leaked outside Home');
        assert.equal(await page.locator('vite-error-overlay').count(), 0);
        report.navigation.push({ lang, href, actualUrl: page.url(), heading: await page.locator('main h1').innerText() });
      }
      await page.setViewportSize({ width: 360, height: 900 });
      report.clinicalFlows.push(await clinicalFlow(page, base, lang));
      await context.close();
    }
  });
  assert.equal(report.errors.length, 0, 'Application page errors');
  report.status = 'PASS';
} catch (error) {
  report.status = 'FAIL';
  report.errors.push(error.message);
  throw error;
} finally {
  writeFileSync(join(destination, 'CLINICAL_MINIMAL_HTTP_QA.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify({ status: report.status, platform: report.platform, states: report.complementaryHeroStates.length,
  navigation: report.navigation.length, realClinicalFlows: report.clinicalFlows.length }));
