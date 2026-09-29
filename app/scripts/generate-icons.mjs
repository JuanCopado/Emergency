// Renders public/favicon.svg into the PNG icons required by the PWA manifest.
import { readFileSync, writeFileSync } from 'node:fs';
import { chromium } from 'playwright-core';
import { chromiumPath } from './chromium.mjs';

const svg = readFileSync(new URL('../public/favicon.svg', import.meta.url), 'utf8');
const targets = [
  { file: 'pwa-192x192.png', size: 192, pad: 0 },
  { file: 'pwa-512x512.png', size: 512, pad: 0 },
  { file: 'apple-touch-icon.png', size: 180, pad: 0 },
  { file: 'maskable-512x512.png', size: 512, pad: 0.12 },
];

const browser = await chromium.launch({ executablePath: chromiumPath() });
const page = await browser.newPage();
for (const t of targets) {
  const inner = Math.round(t.size * (1 - 2 * t.pad));
  const bg = t.pad ? '#0b1220' : 'transparent';
  await page.setViewportSize({ width: t.size, height: t.size });
  await page.setContent(
    `<html><body style="margin:0;background:${bg};display:flex;align-items:center;justify-content:center;width:${t.size}px;height:${t.size}px">` +
      svg.replace('<svg ', `<svg width="${inner}" height="${inner}" `) +
      '</body></html>',
  );
  const buf = await page.screenshot({ omitBackground: !t.pad, clip: { x: 0, y: 0, width: t.size, height: t.size } });
  writeFileSync(new URL(`../public/${t.file}`, import.meta.url), buf);
  console.log('wrote', t.file);
}
await browser.close();
