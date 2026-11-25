// Synthetic local navigation QA; real built app + canonical backend, no patient data.
/* global document */
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { spawn } from 'node:child_process';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { withClinicalApp } from './functional-harness.mjs';
import { ROUTE_CONTRACTS, registeredPaths, matchesRegisteredRoute, assertRouteCoverage } from './route-identity.mjs';
import { assertRouteIdentity, inspectRoute } from './check-route-identity.mjs';

const appRoot = fileURLToPath(new URL('../', import.meta.url));
const output = process.env.ROUTE_QA_OUTPUT;
if (output) rmSync(output, { force: true }); // Never leave a stale PASS on preflight failure.
const patterns = registeredPaths(readFileSync(join(appRoot, 'src/App.tsx'), 'utf8'));
assertRouteCoverage(patterns);
const catalog = JSON.parse(readFileSync(join(appRoot, 'src/data/generatedPediatricOutpatient.json')));
const report = { clinical_status: 'CLINICALLY_PENDING', release_status: 'NO_GO_CLINICAL_RELEASE',
  scope: 'Navigation and functional identity; not diagnostic or accessibility certification',
  limitations: ['Native Windows Edge and Chrome are not inferred from Chromium/Linux results.',
    'Blood gas navigation uses the real local session; native Windows extraction is checked separately.',
    'T06 navigation does not exercise providers or close G05.'],
  provenance: {
    head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: appRoot, encoding: 'utf8' }).trim(),
    dirty: !!execFileSync('git', ['status', '--porcelain'], { cwd: appRoot, encoding: 'utf8' }).trim(),
    sha256: Object.fromEntries(['src/App.tsx', 'src/data/generatedPediatricOutpatient.json',
      'src/pages/PediatricOutpatient.tsx', 'src/test/pediatric-outpatient.test.tsx', 'src/test/route-identity.test.mjs',
      'scripts/check-route-navigation.mjs', 'scripts/check-route-identity.mjs', 'scripts/route-identity.mjs',
      'scripts/functional-harness.mjs', 'dist/index.html',
      ...readdirSync(join(appRoot, 'dist/assets')).sort().map(name => `dist/assets/${name}`),
    ].map(path => [path, createHash('sha256').update(readFileSync(join(appRoot, path))).digest('hex')])),
  },
  routes: [], pediatric_history: [], negative_controls: [], links: [], catalog: {}, errors: [], status: 'RUNNING' };
const screenshots = process.env.ROUTE_QA_SCREENSHOTS;
const bloodGas = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
  'from blood_gas_local import make_server; s=make_server(ui_port=4180); print(s.server_port,flush=True); s.serve_forever()'],
  { cwd: join(appRoot, '../clinical/scripts'), windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });

const bloodGasPort = new Promise((resolve, reject) => {
  const timeout = setTimeout(() => reject(new Error('Local blood gas session startup timeout')), 15000);
  let output = '';
  bloodGas.stdout.on('data', data => {
    output += data;
    if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); }
  });
  bloodGas.stderr.on('data', () => {});
  bloodGas.on('error', error => { clearTimeout(timeout); reject(error); });
  bloodGas.on('exit', code => { clearTimeout(timeout); reject(new Error(`Local blood gas session exited ${code}`)); });
});

function literalLinks(directory) {
  const links = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    if (entry.name === 'test' || entry.name.includes('.test.')) continue;
    const path = join(directory, entry.name);
    if (entry.isDirectory()) links.push(...literalLinks(path));
    else if (/\.tsx?$/.test(path)) {
      const text = readFileSync(path, 'utf8');
      for (const match of text.matchAll(/(?:\b(?:to|href)\s*[=:]\s*|\bnavigate\(\s*)['"](\/[^'"]*)['"]/g)) links.push(match[1]);
    }
  }
  return links;
}

async function checkCatalog(page) {
  const drug = page.getByLabel('Fármaco o combinación');
  const regimen = page.getByLabel('Diagnóstico y régimen');
  await regimen.waitFor();
  const ids = () => regimen.locator('option').evaluateAll(options => options.map(o => o.value).filter(Boolean).sort());
  const checkIds = async expected => {
    await page.waitForFunction(values => {
      const select = document.querySelectorAll('main select')[1];
      return select && JSON.stringify([...select.options].map(o => o.value).filter(Boolean).sort()) === JSON.stringify(values);
    }, expected);
    assert.deepEqual(await ids(), expected);
  };
  await checkIds(catalog.regimens.map(r => r.id).sort());
  for (const group of catalog.drugs) {
    await drug.selectOption(group.id);
    await checkIds(catalog.regimens.filter(r => r.drug_id === group.id).map(r => r.id).sort());
  }
  await drug.selectOption('');
  await regimen.selectOption('paracetamol-pain-fever-home');
  await page.locator('form#pediatric-input').waitFor();
  await page.getByLabel('Edad (meses)', { exact: true }).fill('120');
  assert.equal(await page.getByLabel('Edad (meses)', { exact: true }).inputValue(), '120');
  assert.equal(await page.getByRole('button', { name: 'Comprobar y calcular', exact: true }).isEnabled(), true);
  report.catalog = { regimens: catalog.regimens.length, drug_groups: catalog.drugs.length, all_groups_checked: true, selected_form_interactive: true };
}

async function checkPediatricHistory(page, base, verify) {
  const drug = page.getByLabel('Fármaco o combinación');
  const regimen = page.getByLabel('Diagnóstico y régimen');
  const snapshot = async (mode, expectedDrug, expectedRegimen) => {
    await page.waitForFunction(({ expectedDrug, expectedRegimen }) => {
      const selects = document.querySelectorAll('main select');
      return selects[0]?.value === expectedDrug && selects[1]?.value === expectedRegimen;
    }, { expectedDrug, expectedRegimen });
    assert.equal(await drug.inputValue(), expectedDrug);
    assert.equal(await regimen.inputValue(), expectedRegimen);
    assert.equal(await page.locator('form#pediatric-input').count(), expectedRegimen ? 1 : 0);
    await verify('/pediatrics', `history-${mode}`);
    report.pediatric_history.push({ mode, url: page.url(), drug: await drug.inputValue(), regimen: await regimen.inputValue(), status: 'PASS' });
  };
  await page.goto(base + '/pediatrics');
  await snapshot('direct', '', '');
  await drug.selectOption('paracetamol');
  await regimen.selectOption('paracetamol-pain-fever-home');
  await snapshot('selected-paracetamol', 'paracetamol', 'paracetamol-pain-fever-home');
  await drug.selectOption('fluticasone-propionate');
  await snapshot('filter-fluticasone', 'fluticasone-propionate', '');
  await page.goBack();
  await snapshot('back', 'paracetamol', 'paracetamol-pain-fever-home');
  if (screenshots) await page.screenshot({ path: join(screenshots, 'history-back-paracetamol.png'), fullPage: false });
  await page.goForward();
  await snapshot('forward', 'fluticasone-propionate', '');
  await page.reload();
  await snapshot('reload-filter', 'fluticasone-propionate', '');
  await page.goto(base + '/pediatrics?regimen=paracetamol-pain-fever-home');
  await snapshot('direct-regimen', 'paracetamol', 'paracetamol-pain-fever-home');
  await page.reload();
  await snapshot('reload-regimen', 'paracetamol', 'paracetamol-pain-fever-home');
  await page.getByRole('link', { name: 'Inicio', exact: true }).click();
  await page.locator('a[href="/pediatrics"]').filter({ visible: true }).first().click();
  await snapshot('internal-link', '', '');
}

async function checkBrowserNegatives(page, context, base) {
  const record = (kind, observed) => {
    assert.equal(observed.status, 'FAIL', kind);
    report.negative_controls.push({ kind, expected_valid: false, status: 'REJECTED_INVALID_MODULE', observed });
  };
  await page.route('**/pediatrics?qa=404', route => route.fulfill({ status: 404, contentType: 'text/html', body: readFileSync(join(appRoot, 'dist/index.html'), 'utf8') }));
  try {
    const response = await page.goto(base + '/pediatrics?qa=404');
    const observed = await inspectRoute(page, '/pediatrics', response.status());
    assert.ok(observed.failures.includes('HTTP_ERROR'));
    record('real-http-404-with-module', observed);
  } finally { await page.unroute('**/pediatrics?qa=404'); }

  await page.goto(base + '/pediatrics');
  await page.locator('main select').first().waitFor();
  // Leave one visible select: a correct heading and partial clinical UI must fail.
  await page.locator('main select').last().evaluate(element => element.remove());
  const missing = await inspectRoute(page, '/pediatrics', 200);
  assert.ok(missing.failures.some(failure => failure.startsWith('MISSING_MODULE_CONTROL')));
  record('correct-heading-missing-required-control', missing);

  await page.goto(base + '/pediatrics');
  const errors = [];
  const listener = error => errors.push(error.message);
  page.on('pageerror', listener);
  try {
    const observedError = page.waitForEvent('pageerror');
    await page.evaluate(() => { setTimeout(() => { throw new Error('R92 synthetic browser error'); }, 0); });
    await observedError;
    const observed = await inspectRoute(page, '/pediatrics', 200, errors);
    assert.ok(observed.failures.includes('BROWSER_ERRORS'));
    record('uncaught-browser-error', observed);
  } finally { page.off('pageerror', listener); }

  const broken = await context.newPage();
  const loadErrors = [];
  broken.setDefaultTimeout(1500);
  broken.on('pageerror', error => loadErrors.push(error.message));
  broken.on('console', message => { if (message.type() === 'error') loadErrors.push(message.text()); });
  let aborted = 0;
  await broken.route('**/assets/PediatricOutpatient-*.js', route => { aborted++; return route.abort('failed'); });
  try {
    await broken.goto(base + '/pediatrics');
    await assert.rejects(() => assertRouteIdentity(broken, '/pediatrics', 200, loadErrors));
    assert.ok(aborted > 0, 'The pediatric chunk must actually have been blocked');
    assert.ok(loadErrors.length > 0, 'The failed load must be observed by the real browser');
    report.negative_controls.push({ kind: 'aborted-pediatric-module-load', expected_valid: false, status: 'REJECTED_LOAD_FAILURE', aborted_requests: aborted, errors: loadErrors });
  } finally { await broken.close(); }
}

try {
  const bloodPort = await bloodGasPort;
  await withClinicalApp(async ({ page, context, base, browser }) => {
    report.browser = browser.version();
    let errors = [], documentStatus = null;
    const links = new Set(literalLinks(join(appRoot, 'src')));
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('response', response => {
      if (response.request().isNavigationRequest() && response.frame() === page.mainFrame()) documentStatus = response.status();
    });
    const verify = async (path, mode) => {
      const row = await assertRouteIdentity(page, path, documentStatus, errors);
      for (const href of await page.locator('a[href]').evaluateAll(elements => elements.map(el => el.href))) {
        const url = new URL(href);
        if (url.origin === base) links.add(url.pathname + url.search);
      }
      report.routes.push({ ...row, mode, viewport: page.viewportSize() });
    };
    const goto = async path => { errors = []; await page.goto(base + path); };
    for (const contract of ROUTE_CONTRACTS) {
      await goto(contract.example); await verify(contract.example, 'direct');
      errors = []; await page.reload(); await verify(contract.example, 'reload');
      const parent = contract.example === '/acute-medications' ? '/drugs'
        : contract.pattern.includes(':id') ? contract.example.slice(0, contract.example.lastIndexOf('/')) : contract.example === '/' ? '/settings' : '/';
      await goto(parent);
      await page.locator(`a[href="${contract.example}"]`).filter({ visible: true }).first().click();
      await verify(contract.example, 'internal');
      errors = []; await page.goBack(); await verify(parent, 'back');
      errors = []; await page.goForward(); await verify(contract.example, 'forward');
    }
    await goto('/pediatrics'); await verify('/pediatrics', 'catalog-ready');
    if (screenshots) {
      mkdirSync(screenshots, { recursive: true });
      await page.screenshot({ path: join(screenshots, 'pediatrics-desktop.png'), fullPage: false });
    }
    await checkCatalog(page);
    await page.reload(); await page.locator('form#pediatric-input').waitFor();
    assert.equal(await page.getByLabel('Diagnóstico y régimen').inputValue(), 'paracetamol-pain-fever-home');
    await page.setViewportSize({ width: 375, height: 812 });
    await verify('/pediatrics', 'mobile-selected-form');
    if (screenshots) {
      mkdirSync(screenshots, { recursive: true });
      await page.screenshot({ path: join(screenshots, 'pediatrics-mobile.png'), fullPage: false });
    }
    await page.setViewportSize({ width: 1280, height: 720 });
    await checkPediatricHistory(page, base, verify);
    for (const [path, expected] of [['/pediatric-outpatient', '/pediatrics'], ['/clinical-scores', '/scores'], ['/no-such-route', '/'], ['/drugs/unknown', '/drugs/norepinephrine'], ['/guides/unknown', '/guides/sepsis-shock'], ['/clinical/unknown', '/clinical/sepsis-shock'], ['/procedures/unknown', '/procedures/PROC-VASC-007']]) {
      await goto(path);
      const row = await inspectRoute(page, expected, documentStatus, errors);
      assert.equal(row.status, 'FAIL'); assert.ok(row.failures.includes('NOT_FOUND_PAGE'), path);
      report.negative_controls.push({ requested_route: path, expected_valid: false, status: 'REJECTED_INVALID_ROUTE', observed: row });
    }
    await checkBrowserNegatives(page, context, base);
    report.links = [...links].sort().map(path => ({ path, registered: matchesRegisteredRoute(path, patterns) }));
    assert.deepEqual(report.links.filter(link => !link.registered), [], 'Navigation targets must match a registered non-wildcard route');
    report.status = 'PASS';
  }, { '/api/blood-gas': { target: `http://127.0.0.1:${bloodPort}`, changeOrigin: true } });
} catch (error) {
  report.status = 'FAIL'; report.errors.push(String(error)); process.exitCode = 1;
} finally {
  bloodGas.kill();
  if (output) { mkdirSync(dirname(output), { recursive: true }); writeFileSync(output, JSON.stringify(report, null, 2) + '\n'); }
  console.log(JSON.stringify(report));
}
