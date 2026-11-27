// Focal browser regression for approved structural/reference changes only.
import assert from 'node:assert/strict';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { withClinicalApp } from './functional-harness.mjs';

assert(process.env.CARDIO_FOLLOWUP_QA_OUTPUT, 'Set CARDIO_FOLLOWUP_QA_OUTPUT');
const output = resolve(process.env.CARDIO_FOLLOWUP_QA_OUTPUT);
mkdirSync(output, { recursive: true });
const report = { status: 'RUNNING', platform: process.platform, cases: [], errors: [] };
try {
  await withClinicalApp(async ({ context, page, base, browser }) => {
    report.browser = browser.version();
    page.on('pageerror', error => report.errors.push(error.message));
    for (const lang of ['es', 'pt', 'en', 'zh']) {
      const copy = JSON.parse(readFileSync(new URL(`../src/i18n/locales/${lang}.clinical.json`, import.meta.url), 'utf8'));
      const ui = key => copy[key] || key;
      await context.addInitScript(value => localStorage.setItem('emergency.lang', value), lang);
      await page.setViewportSize({ width: 360, height: 900 });
      for (const route of ['/clinical', '/guides']) {
        await page.goto(`${base}${route}/arrhythmias-cardiac-arrest`);
        const table = page.getByRole('table', { name: ui('Monitorización según el contexto de reanimación') });
        await table.waitFor();
        assert.equal(await table.getByRole('row').count(), 5);
        assert.equal(await page.locator('#resuscitation-circuits a').count(), 4);
        await page.goto(`${base}${route}/non-coronary-chest-pain`);
        const auxiliary = page.getByRole('navigation', { name: ui('Reevaluación y destino') });
        await auxiliary.waitFor();
        await auxiliary.getByRole('link').click();
        await page.waitForURL(`${base}${route}/observation-discharge`);
        await auxiliary.waitFor({ state: 'detached' });
        await page.goto(`${base}${route}/iv-antihypertensive-selection`);
        const panel = page.getByRole('region', { name: ui('Referencia informativa de antihipertensivos IV') });
        const controls = panel.getByRole('combobox');
        await panel.waitFor();
        assert.equal(await controls.nth(1).inputValue(), '');
        await controls.nth(1).selectOption('PT');
        for (const [drug, registration] of [['labetalol', '5767504'], ['esmolol', '5303045'], ['nitroglycerin', '2585081']]) {
          await controls.nth(0).selectOption(drug);
          assert((await panel.getByRole('article').innerText()).includes(registration));
          assert.equal(await panel.locator('input, output, button').count(), 0);
        }
        assert(await page.evaluate(() => globalThis.document.documentElement.scrollWidth <= globalThis.innerWidth + 1), 'Mobile overflow');
        await panel.screenshot({ path: join(output, `${lang}-${route.slice(1)}-pt-reference.png`) });
        for (const drug of ['nicardipine', 'clevidipine', 'hydralazine', 'nitroprusside']) {
          await controls.nth(0).selectOption(drug);
          assert.equal(await panel.getByRole('article').count(), 0);
        }
        report.cases.push({ lang, route, width: 360, monitoringRows: 4, algorithms: 4, observation: 'manual navigation PASS', ptIdentities: 3, unknownDrugs: 4, administrationControls: 0 });
      }
    }
  });
  assert.equal(report.errors.length, 0);
  report.status = 'PASS';
} catch (error) {
  report.status = 'FAIL';
  report.errors.push(error.message);
  throw error;
} finally {
  writeFileSync(join(output, 'CARDIO_BROWSER_QA.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify({ status: report.status, cases: report.cases.length, platform: report.platform }));
