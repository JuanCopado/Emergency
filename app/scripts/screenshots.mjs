// Takes review screenshots of the production build (run `npm run build` first).
// Usage: node scripts/screenshots.mjs  → screenshots/*.png
import { mkdirSync } from 'node:fs';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const PORT = 4173;
const BASE = `http://localhost:${PORT}`;
const OUT = new URL('../screenshots/', import.meta.url).pathname;
mkdirSync(OUT, { recursive: true });

const server = await preview({ preview: { port: PORT, strictPort: true }, logLevel: 'warn' });

const shots = [
  { name: 'home-dark-es', path: '/', theme: 'dark', lang: 'es' },
  { name: 'calculator-norepinephrine-70kg-light-es', path: '/calculator?drug=norepinephrine&weight=70&dose=0.05', theme: 'light', lang: 'es' },
  { name: 'drug-detail-dark-zh', path: '/drugs/norepinephrine', theme: 'dark', lang: 'zh' },
];
const viewports = [
  { tag: 'mobile', width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  { tag: 'desktop', width: 1440, height: 900, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
];

const browser = await chromium.launch({ executablePath: chromiumPath() });
try {
  for (const vp of viewports) {
    for (const s of shots) {
      const ctx = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        deviceScaleFactor: vp.deviceScaleFactor,
        isMobile: vp.isMobile,
        hasTouch: vp.hasTouch,
        colorScheme: s.theme,
        serviceWorkers: 'block',
      });
      await ctx.addInitScript(
        ([theme, lang]) => {
          localStorage.setItem('emergency.theme', theme);
          localStorage.setItem('emergency.lang', lang);
        },
        [s.theme, s.lang],
      );
      const page = await ctx.newPage();
      const errors = [];
      page.on('pageerror', (e) => errors.push(e.message));
      page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
      await page.goto(BASE + s.path, { waitUntil: 'networkidle' });
      await page.waitForTimeout(300);
      const file = `${OUT}${s.name}-${vp.tag}.png`;
      await page.screenshot({ path: file, fullPage: false });
      await page.screenshot({ path: file.replace('.png', '-full.png'), fullPage: true });
      console.log('saved', file, errors.length ? `ERRORS: ${errors.join(' | ')}` : '');
      await ctx.close();
    }
  }
} finally {
  await browser.close();
  await server.close();
}
