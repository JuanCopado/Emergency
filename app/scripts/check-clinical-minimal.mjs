// Synthetic presentation QA. No patient input or clinical API invocation.
/* global document, getComputedStyle, innerWidth */
import assert from 'node:assert/strict';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { extname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';

const interceptedBuild = process.env.MINIMAL_QA_DIST === '1';
const base = interceptedBuild ? 'https://emergency.test' : process.env.MINIMAL_QA_URL || 'http://127.0.0.1:4192';
const dist = fileURLToPath(new URL('../dist/', import.meta.url));
const output = process.env.MINIMAL_QA_OUTPUT;
assert(output, 'MINIMAL_QA_OUTPUT must name an evidence directory');
mkdirSync(output, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
});
const report = { scope: 'Opt-in home token slice; not full prototype fidelity or clinical validation',
  transport: interceptedBuild ? 'Built artifacts fulfilled by Playwright; no HTTP server/network exercised' : 'HTTP server',
  status: 'RUNNING', browser: browser.version(), states: [], errors: [] };
try {
  for (const lang of ['es', 'pt', 'en', 'zh']) {
    for (const theme of ['light', 'dark']) {
      for (const width of [360, 1366]) {
        const context = await browser.newContext({ viewport: { width, height: 1000 }, reducedMotion: 'reduce' });
        const page = await context.newPage();
        if (interceptedBuild) {
          await page.route('**/*', route => {
            const url = new URL(route.request().url());
            if (url.origin !== base) return route.abort();
            const path = resolve(dist, `.${decodeURIComponent(url.pathname)}`);
            if (path !== resolve(dist) && !path.startsWith(resolve(dist) + sep)) return route.abort();
            const asset = existsSync(path) && extname(path) ? path : join(dist, 'index.html');
            const mime = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
              '.json': 'application/json', '.webmanifest': 'application/manifest+json',
              '.svg': 'image/svg+xml', '.png': 'image/png', '.html': 'text/html' };
            return route.fulfill({ body: readFileSync(asset), contentType: mime[extname(asset)] || 'application/octet-stream' });
          });
        }
        page.on('pageerror', error => report.errors.push(error.message));
        await page.addInitScript(({ lang, theme }) => {
          localStorage.setItem('emergency.lang', lang);
          localStorage.setItem('emergency.theme', theme);
        }, { lang, theme });
        await page.goto(base, { waitUntil: 'networkidle' });
        assert.equal(await page.locator('.clinical-minimal-preview').count(), 0);
        const linksBefore = await page.locator('main a').evaluateAll(links => links.map(link => link.getAttribute('href')));
        const textBefore = await page.locator('main').innerText();
        await page.goto(`${base}/?design=clinical-minimal`, { waitUntil: 'networkidle' });
        assert.equal(await page.locator('.clinical-minimal-preview').count(), 1);
        assert.deepEqual(await page.locator('main a').evaluateAll(links => links.map(link => link.getAttribute('href'))), linksBefore);
        assert.equal(await page.locator('main').innerText(), textBefore);
        const appearance = await page.locator('.clinical-minimal-preview').evaluate(element => ({
          background: getComputedStyle(element).backgroundColor,
          color: getComputedStyle(element).color,
          horizontalOverflow: document.documentElement.scrollWidth > innerWidth,
          htmlLang: document.documentElement.lang,
        }));
        assert.equal(appearance.background, theme === 'dark' ? 'rgb(11, 20, 32)' : 'rgb(245, 247, 250)');
        assert.equal(appearance.horizontalOverflow, false);
        assert.equal(appearance.htmlLang, ({ es: 'es', pt: 'pt-PT', en: 'en', zh: 'zh-Hans' })[lang]);
        await page.locator('#home-search').focus();
        await page.keyboard.press('Tab');
        const focusWidth = await page.evaluate(() => getComputedStyle(document.activeElement).outlineWidth);
        assert.equal(focusWidth, '3px');
        if (lang === 'es' && theme === 'light' || lang === 'pt' && theme === 'dark') {
          await page.screenshot({ path: join(output, `${width}-${theme}-${lang}.png`), fullPage: true });
        }
        // Reuse the real home search flow and check presentation cannot leak into other pages.
        await page.locator('#home-search').fill('noradrenaline');
        await page.locator('#home-search').press('Enter');
        await page.waitForURL('**/drugs?q=noradrenaline');
        await page.locator('.clinical-minimal-preview').waitFor({ state: 'detached' });
        assert.equal(await page.locator('.clinical-minimal-preview').count(), 0);
        report.states.push({ lang, theme, width, ...appearance, links: linksBefore.length, search: 'PASS', focusWidth });
        await context.close();
      }
    }
  }
  assert.equal(report.errors.length, 0);
  report.status = 'PASS';
} catch (error) {
  report.status = 'FAIL';
  report.errors.push(error.message);
  throw error;
} finally {
  await browser.close();
  writeFileSync(join(output, 'CLINICAL_MINIMAL_BROWSER_QA.json'), `${JSON.stringify(report, null, 2)}\n`);
}
console.log(JSON.stringify({ status: report.status, states: report.states.length, errors: report.errors.length }));
