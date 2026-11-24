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
      'scripts/check-route-navigation.mjs', 'scripts/check-route-identity.mjs', 'scripts/route-identity.mjs',
      'scripts/functional-harness.mjs', 'dist/index.html',
      ...readdirSync(join(appRoot, 'dist/assets')).sort().map(name => `dist/assets/${name}`),
    ].map(path => [path, createHash('sha256').update(readFileSync(join(appRoot, path))).digest('hex')])),
  },
  routes: [], negative_controls: [], links: [], catalog: {}, errors: [], status: 'RUNNING' };
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

try {
  const bloodPort = await bloodGasPort;
  await withClinicalApp(async ({ page, base, browser }) => {
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
    for (const [path, expected] of [['/pediatric-outpatient', '/pediatrics'], ['/clinical-scores', '/scores'], ['/no-such-route', '/'], ['/drugs/unknown', '/drugs/norepinephrine'], ['/guides/unknown', '/guides/sepsis-shock'], ['/clinical/unknown', '/clinical/sepsis-shock'], ['/procedures/unknown', '/procedures/PROC-VASC-007']]) {
      await goto(path);
      const row = await inspectRoute(page, expected, documentStatus, errors);
      assert.equal(row.status, 'FAIL'); assert.ok(row.failures.includes('NOT_FOUND_PAGE'), path);
      report.negative_controls.push({ requested_route: path, expected_valid: false, status: 'REJECTED_INVALID_ROUTE', observed: row });
    }
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
