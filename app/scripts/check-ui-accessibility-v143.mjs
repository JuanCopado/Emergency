/* global document, getComputedStyle */
import assert from 'node:assert/strict';
import { writeFileSync } from 'node:fs';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const report = { scope: 'Representative theme tokens and keyboard paths; not an accessibility certification', themes: [], keyboard: [] };
let server, browser;
try {
  server = await preview({ preview: { host: '127.0.0.1', port: 4177, strictPort: true }, logLevel: 'error' });
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
  const page = await browser.newPage({ viewport: { width: 375, height: 812 }, serviceWorkers: 'block' });
  await page.addInitScript(() => { localStorage.setItem('emergency.theme', 'light'); localStorage.setItem('emergency.lang', 'es'); });
  await page.goto('http://127.0.0.1:4177/', { waitUntil: 'networkidle' });
  for (const theme of ['light', 'dark']) {
    if (theme === 'dark') { await page.getByRole('button', { name: 'Cambiar a tema oscuro' }).click(); await page.waitForTimeout(300); }
    const ratios = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      const luminance = key => style.getPropertyValue('--c-' + key).trim().split(/\s+/).map(Number).map(n => n / 255).map(n => n <= .04045 ? n / 12.92 : ((n + .055) / 1.055) ** 2.4).reduce((sum, n, i) => sum + n * [.2126, .7152, .0722][i], 0);
      return [['fg','bg'],['muted','bg'],['primary-fg','primary'],['warn','warn-bg'],['danger','surface']].map(([a,b]) => { const x = luminance(a), y = luminance(b); return { pair: `${a}/${b}`, ratio: Number(((Math.max(x,y)+.05)/(Math.min(x,y)+.05)).toFixed(2)) }; });
    });
    report.themes.push({ theme, ratios });
  }
  await page.locator('main').focus();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement?.textContent), 'Nota clínica');
  await page.keyboard.press('Enter');
  await page.getByLabel('Idade', { exact: true }).waitFor();
  for (const [tab, field] of [['Exame','Exploração'],['Problemas','Problemas'],['Plano','Plano médico']]) {
    const button = page.getByRole('button', { name: tab, exact: true });
    await button.focus(); await page.keyboard.press('Enter');
    assert.equal(await page.getByLabel(field, { exact: true }).count(), 1);
    report.keyboard.push({ tab, field, result: 'PASS' });
  }
  await page.getByRole('button', { name: 'Exportar', exact: true }).focus();
  await page.keyboard.press('Enter');
  assert(await page.getByRole('button', { name: 'JSON', exact: true }).isDisabled());
  report.keyboard.push({ path: 'Home → nota → pestañas → exportación bloqueada', result: 'PASS' });
  console.log(JSON.stringify(report));
} finally {
  await browser?.close();
  if (server) await new Promise(resolve => server.httpServer.close(resolve));
  writeFileSync(new URL('../../clinical/qa/assets/v1.43/after/accessibility.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
}
