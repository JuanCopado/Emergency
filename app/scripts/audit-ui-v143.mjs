// Local, synthetic UI inspection. Build first; no external services or patient data.
/* global document, innerWidth */
import { mkdirSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const phase = process.argv[2];
if (!['before', 'after'].includes(phase)) throw new Error('Use before or after');
const output = process.argv[3] ? resolve(process.argv[3]) + sep
  : fileURLToPath(new URL(`../../clinical/qa/assets/v1.43/${phase}/`, import.meta.url));
mkdirSync(output, { recursive: true });
const routes = [
  ['home', '/', 'Apoyo clínico para urgencias y cuidados agudos'],
  ['note', '/clinical-note', 'Apoyo al diagnóstico'],
  ['drugs', '/drugs', 'Fármacos'],
  ['drug', '/drugs/norepinephrine', 'Norepinephrine'],
  ['calculator', '/calculator?drug=norepinephrine&weight=70&dose=0.05', 'Calculadora de perfusiones'],
  ['pediatrics', '/pediatrics?regimen=paracetamol-pain-fever-home', 'Pediatría ambulatoria'],
  ['clinical', '/clinical', 'Patologías y módulos'],
  ['sepsis', '/clinical/sepsis-shock', 'Sepsis Shock'],
  ['guides', '/guides', 'Pantalla completa · impresión · PDF'],
  ['guide', '/guides/sepsis-shock', 'Sepsis Shock'],
  ['scores', '/clinical/clinical-scores-calculators', 'Clinical Scores Calculators'],
  ['pocus', '/clinical/pocus', 'Pocus'],
  ['ecg', '/clinical/ecg-image', 'Ecg Image'],
  ['procedures', '/procedures', 'Procedimientos'],
  ['pilot', '/procedures/PROC-VASC-007', 'Catéter venoso central femoral ecoguiado'],
  ['settings', '/settings', 'Ajustes'],
  ['about', '/about', 'Acerca de y aviso legal'],
  ['not-found', '/route-does-not-exist', 'Página no encontrada'],
  ['unknown-module', '/clinical/unknown', 'Módulo no encontrado'],
  ['unknown-guide', '/guides/unknown', 'Guía no encontrada'],
  ['acute-medications', '/acute-medications', 'Farmacología aguda'],
  ['insulin-uci', '/insulin-uci', 'Insulinoterapia UCI'],
  ['score-calculator', '/scores', 'Scores clínicos'],
  ['blood-gas', '/blood-gas', 'Revisión de gasometrías'],
  ['t06-lab', '/t06-lab', 'Laboratorio T06 en localhost'],
];
const viewports = [[1366,768], [1920,1080], [768,1024], [1024,768], [375,812], [430,932]];
const shots = new Set(['home', 'note', 'procedures', 'pediatrics', 'scores', 'pilot', 'drug']);
const report = { phase, url: 'http://127.0.0.1:4175', browser: '', results: [] };
let server, browser;
try {
  server = await preview({ preview: { host: '127.0.0.1', port: 4175, strictPort: true }, logLevel: 'error' });
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  report.browser = browser.version();
  for (const [width, height] of viewports) {
    const context = await browser.newContext({ viewport: { width, height }, serviceWorkers: 'block', colorScheme: 'light' });
    await context.addInitScript(() => {
      localStorage.setItem('emergency.theme', 'light'); localStorage.setItem('emergency.lang', 'es');
    });
    const page = await context.newPage();
    let errors = [], warnings = [], resources = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); if (m.type() === 'warning') warnings.push(m.text()); });
    page.on('response', r => { if (r.status() >= 400) resources.push({ url: r.url(), status: r.status() }); });
    for (const [name, route, title] of routes) {
      errors = []; warnings = []; resources = [];
      await page.goto(report.url + route, { waitUntil: 'networkidle' });
      await page.locator('main').getByRole('heading', { level: 1, name: title, exact: true }).waitFor();
      const expected = new URL(route, report.url);
      const actual = new URL(page.url());
      assert.equal(actual.origin + actual.pathname, expected.origin + expected.pathname);
      for (const [key, value] of expected.searchParams) assert.equal(actual.searchParams.get(key), value, route);
      if (name === 'pediatrics') {
        const regimen = new URL(page.url()).searchParams.get('regimen');
        const filter = page.getByLabel('Fármaco o combinación');
        const selection = page.getByLabel('Diagnóstico y régimen');
        assert.equal(await selection.inputValue(), regimen);
        await filter.selectOption('fluticasone-propionate');
        assert.equal(await selection.inputValue(), '');
        await page.goBack();
        await filter.locator('option[value=paracetamol]:checked').waitFor({ state: 'attached' });
        assert.equal(await filter.inputValue(), 'paracetamol');
        assert.equal(await selection.inputValue(), regimen);
        await page.goForward();
        await filter.locator('option[value=fluticasone-propionate]:checked').waitFor({ state: 'attached' });
        assert.equal(await filter.inputValue(), 'fluticasone-propionate');
        assert.equal(await selection.inputValue(), '');
        await page.goBack();
        await filter.locator('option[value=paracetamol]:checked').waitFor({ state: 'attached' });
      }
      const data = await page.evaluate(() => {
        const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
        const controls = [...document.querySelectorAll('input, select, textarea, button')].filter(visible);
        const unnamed = controls.filter(el => !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby') && !el.labels?.length && !(el.innerText || '').trim()).map(el => ({ tag: el.tagName, placeholder: el.getAttribute('placeholder') }));
        const overflow = [...document.querySelectorAll('main *, header *')].filter(visible).filter(el => {
          const b = el.getBoundingClientRect(); return b.right > innerWidth + 1 && !el.closest('.overflow-x-auto');
        }).slice(0, 8).map(el => ({ tag: el.tagName, text: el.textContent.slice(0, 100) }));
        const small = [...document.querySelectorAll('button,a,select,input:not([type=checkbox]):not([type=radio])')].filter(visible).filter(el => { const b = el.getBoundingClientRect(); return b.height < 44 || b.width < 44; }).length;
        return { title: document.querySelector('main h1')?.textContent, documentWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth, unnamed, overflow, smallTargets: small, loadMs: Math.round(performance.getEntriesByType('navigation')[0].loadEventEnd), brokenImages: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).length };
      });
      report.results.push({ name, route, width, height, ...data, errors: [...errors], warnings: [...warnings], resources: [...resources] });
      if (phase === 'after') {
        assert(data.documentWidth <= width, `${route} overflows at ${width}: ${data.documentWidth}`);
        assert.deepEqual(data.unnamed, [], `${route} has unnamed controls`);
        assert.deepEqual(errors, [], `${route} has browser errors`);
        assert.deepEqual(resources, [], `${route} has broken resources`);
        assert.equal(data.brokenImages, 0);
      }
      if (shots.has(name) && [375,1366].includes(width)) await page.screenshot({ path: `${output}${name}-${width}.webp`, type: 'webp', quality: 65, fullPage: false });
    }
    if (phase === 'after' && [375,1366].includes(width)) {
      for (const id of ['PROC-VASC-007','PROC-VASC-006','PROC-VASC-010','PROC-AIR-015','PROC-THX-003','PROC-CV-006','PROC-CV-001','PROC-CV-004','PROC-TRA-004','PROC-ORTHO-001']) {
        await page.goto(report.url + '/procedures/' + id, { waitUntil: 'networkidle' });
        await page.getByRole('region', { name: 'STOP', exact: true }).waitFor();
        await page.screenshot({ path: `${output}${id}-${width}.webp`, type: 'webp', quality: 65, fullPage: true });
      }
      await page.goto(report.url + '/procedures');
      await page.getByLabel('Nombre o PROC-ID').fill('femoral');
      await page.getByRole('status').filter({ hasText: '3 procedimientos' }).waitFor();
      await page.getByLabel('Nombre o PROC-ID').fill('PROC-VASC-007');
      await page.getByRole('link', { name: /Catéter venoso central femoral/ }).click();
      await page.getByRole('link', { name: 'STOP', exact: true }).click();
      const stopTop = await page.getByRole('region', { name: 'STOP', exact: true }).evaluate(el => el.getBoundingClientRect().top);
      report.results.push({ name: 'procedure-search-and-stop', width, stopTop });
    }
    await page.goto(report.url + '/', { waitUntil: 'networkidle' });
    await page.locator('main').focus();
    await page.keyboard.press('Tab');
    report.results.push({ name: 'keyboard', width, focused: await page.evaluate(() => ({ tag: document.activeElement?.tagName, text: document.activeElement?.textContent?.trim() })) });
    if (phase === 'after' && [375,1366].includes(width)) {
      await page.getByRole('button', { name: /Cambiar a tema oscuro/ }).click();
      await page.waitForTimeout(300); // Let the existing theme color transition settle.
      await page.screenshot({ path: `${output}home-dark-${width}.webp`, type: 'webp', quality: 65 });
    }
    await context.close();
    console.log(`Inspected ${routes.length} routes at ${width}x${height}`);
  }
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.httpServer.close(resolve));
  writeFileSync(`${output}results.json`, JSON.stringify(report, null, 2) + '\n');
}
