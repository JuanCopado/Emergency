// R10 · PWA offline check (synthetic only). Installs the real service worker from a production build,
// then CUTS the connection (the preview server is stopped AND the browser is put offline) and walks
// the routes that claim to work without a server. It also asserts that `/api/*` never receives the
// application shell, neither from fetch() nor from a top-level navigation.
//
// Usage (after `vite build`): PWA_CHECK_DIST=dist node scripts/check-pwa-offline.mjs
// Not a clinical check: it reads no patient data and exercises no clinical API.
import assert from 'node:assert/strict';
import { resolve } from 'node:path';
import { chromium } from 'playwright-core';
import { preview } from 'vite';
import { chromiumPath } from './chromium.mjs';

const dist = resolve(process.env.PWA_CHECK_DIST ?? 'dist');
const server = await preview({ preview: { host: '127.0.0.1', port: 0 }, build: { outDir: dist }, logLevel: 'error' });
const base = server.resolvedUrls.local[0];
const origin = new URL(base).origin;
const results = [];
const record = (name, detail = '') => results.push(`ok  ${name}${detail ? ` — ${detail}` : ''}`);
let browser;
let failure;

try {
  browser = await chromium.launch({ executablePath: chromiumPath(), headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext();
  await context.addInitScript(() => { try { localStorage.setItem('emergency.lang', 'en'); } catch { /* ignore */ } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));

  // 1. Online: install the worker and wait for the precache; the worker must control the page.
  await page.goto(base);
  await page.evaluate(async () => { await navigator.serviceWorker.ready; });
  await page.waitForFunction(() => navigator.serviceWorker.controller !== null, null, { timeout: 15000 });
  const precached = await page.evaluate(async () => {
    const names = (await caches.keys()).filter((name) => name.includes('precache'));
    let count = 0;
    for (const name of names) count += (await (await caches.open(name)).keys()).length;
    return count;
  });
  assert.ok(precached >= 30, `precache has ${precached} entries`);
  record('service worker installed and controlling the page', `${precached} precached entries`);

  // 2. Online baseline: an API fetch must not be answered with HTML (the boundary answers JSON).
  const online = await page.evaluate(async () => {
    const response = await fetch('/api/clinical-scores/x', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
    return { type: response.headers.get('content-type') ?? '', status: response.status };
  });
  assert.ok(!online.type.includes('text/html'), `online /api fetch returned ${online.type}`);
  record('online /api fetch is not the shell', `${online.status} ${online.type}`);

  // 3. Cut the connection for real: stop the server, then emulate offline.
  await new Promise((done) => server.httpServer.close(done));
  await context.setOffline(true);
  const probe = await page.evaluate(async (target) => {
    try { await fetch(`${target}/__probe__`, { cache: 'no-store' }); return 'reachable'; } catch { return 'unreachable'; }
  }, origin);
  assert.equal(probe, 'unreachable');
  record('connection is really interrupted (server stopped and browser offline)');

  // 4. Local routes still open from the cache.
  const routes = [
    ['/', null],
    ['/drugs', null],
    ['/guides', null],
    ['/procedures', null],
    ['/settings', null],
    ['/about', null],
    ['/calculator?drug=norepinephrine&weight=70&dose=0.05', 'rate-display'],
  ];
  for (const [path, testId] of routes) {
    const response = await page.goto(`${origin}${path}`, { waitUntil: 'domcontentloaded' });
    assert.ok(response && response.ok(), `${path} did not load offline`);
    await page.locator('#root > *').first().waitFor({ timeout: 10000 });
    if (testId) {
      await page.getByTestId(testId).waitFor({ timeout: 10000 });
      assert.equal(await page.getByTestId(testId).innerText(), '5.3', 'local infusion result offline');
    }
    record(`offline route ${path.split('?')[0]}`);
  }
  const notFound = await page.goto(`${origin}/no-such-route`, { waitUntil: 'domcontentloaded' });
  assert.ok(notFound && notFound.ok());
  await page.locator('#root > *').first().waitFor({ timeout: 10000 });
  record('offline unknown route is handled by the app');

  // 5. /api must never be answered with the shell.
  const apiFetch = await page.evaluate(async () => {
    try {
      const response = await fetch('/api/clinical-scores/x', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
      return { settled: 'resolved', type: response.headers.get('content-type') ?? '', status: response.status };
    } catch (error) { return { settled: 'rejected', name: error.name }; }
  });
  assert.ok(apiFetch.settled === 'rejected' || !String(apiFetch.type).includes('text/html'),
    `offline /api fetch was answered with ${JSON.stringify(apiFetch)}`);
  record('offline /api fetch fails (is not answered with the shell)', JSON.stringify(apiFetch));

  const apiPaths = ['/api/clinical-note/analyze', '/api/acute-medications/calc', '/api/pediatric-outpatient/calculate'];
  for (const path of apiPaths) {
    const shell = await page.goto(`${origin}${path}`, { waitUntil: 'domcontentloaded' }).then(
      async (response) => ({ ok: response?.ok() ?? false, root: await page.locator('#root').count() && (await page.locator('#root > *').count()) > 0 }),
      () => ({ ok: false, root: false }),
    );
    assert.ok(!(shell.ok && shell.root), `navigation to ${path} was answered with the application shell`);
    record(`offline navigation to ${path} is not the shell`);
  }
  assert.deepEqual(pageErrors, [], 'page errors while offline');
  record('no page errors while offline');
} catch (error) {
  failure = error;
} finally {
  if (browser) await browser.close();
  await new Promise((done) => (server.httpServer.listening ? server.httpServer.close(done) : done()));
}
for (const line of results) console.log(line);
if (failure) {
  console.error(`FAIL ${failure.message}`);
  process.exitCode = 1;
} else {
  console.log(`PWA offline check passed (${results.length} checks, dist=${dist})`);
}
