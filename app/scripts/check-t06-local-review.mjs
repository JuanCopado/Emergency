// Real Chromium checks against the composed app and its synthetic loopback TLS lab.
// This script never replaces a response, supplies metadata to Q4, or opens a provider link.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { access, mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as pause } from 'node:timers/promises';
import { chromium } from 'playwright-core';

const root = fileURLToPath(new URL('../../', import.meta.url));
const base = new URL(process.env.T06_APP_URL || 'http://127.0.0.1:5173/');
assert.equal(base.protocol, 'http:', 'The composed app must use local HTTP');
assert.ok(['127.0.0.1', 'localhost'].includes(base.hostname), 'Only an explicit loopback app is allowed');
assert.equal(base.username + base.password + base.search + base.hash, '', 'Do not supply credentials or query parameters');
assert.equal(base.pathname, '/', 'T06_APP_URL must name the app root');
assert.ok(process.env.CHROMIUM_PATH, 'Set CHROMIUM_PATH to an installed Chromium executable');
assert.ok(process.env.T06_BACKEND_EVIDENCE_DIR, 'Set T06_BACKEND_EVIDENCE_DIR to this running lab session');
const backendDirectory = path.resolve(process.env.T06_BACKEND_EVIDENCE_DIR);
await access(process.env.CHROMIUM_PATH);
await access(backendDirectory);
const stamp = new Date().toISOString().replaceAll(/[:.]/g, '-');
const output = path.resolve(process.env.T06_BROWSER_OUT || path.join(root, '.local-review', `t06-browser-${stamp}`));
await mkdir(output, { recursive: true });
await mkdir(path.join(output, 'backend-receipts'), { recursive: true });

const cases = [
  { id: 'success', service: 'europe_pmc', phase: 'success', status: 200, rows: 2 },
  { id: 'pubmed', service: 'pubmed', phase: 'success', status: 200, rows: 2 },
  { id: 'nvd', service: 'nvd', phase: 'success', status: 200, rows: 1 },
  { id: 'combined_limits', service: 'nvd', phase: 'success', status: 200, rows: 50 },
  { id: 'empty', service: 'europe_pmc', phase: 'success', status: 200, rows: 0 },
  { id: 'long_text', service: 'europe_pmc', phase: 'success', status: 200, rows: 2 },
  { id: 'limit50', service: 'europe_pmc', phase: 'success', status: 200, rows: 50 },
  { id: 'limit51', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'unsafe_unicode', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'invalid_json', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'invalid_utf8', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'http_error', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'redirect', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'oversize', service: 'europe_pmc', phase: 'error', status: 502, rows: 0 },
  { id: 'timeout', service: 'europe_pmc', phase: 'error', status: 504, rows: 0 },
  { id: 'client_timeout', service: 'europe_pmc', phase: 'timeout', status: null, rows: 0 },
  { id: 'retry_429', service: 'europe_pmc', phase: 'success', status: 200, rows: 2 },
  { id: 'invalid_normalized', service: 'europe_pmc', phase: 'rejected', status: 200, rows: 0 },
];
const states = {
  idle: 'Preparado para ejecutar', loading: 'Ejecutando circuito local…',
  success: 'Respuesta recibida y aceptada por Q4', rejected: 'Contrato rechazado por Q4',
  error: 'Error controlado', timeout: 'Plazo del navegador agotado', cancelled: 'Consulta cancelada',
};
const network = [];
const blockedDestinations = [];
const pageErrors = [];
const consoleErrors = [];
const report = {
  verdict: 'RUNNING', clinical_status: 'CLINICALLY_PENDING', synthetic_only: true,
  method: 'Playwright Chromium, real composed application, real R6/B1 loopback TLS; no response mocks',
  started_utc: new Date().toISOString(), app_url: base.href, backend_evidence_dir: backendDirectory,
  chromium_path: process.env.CHROMIUM_PATH, cases: [], state_checks: [], source_sha256: {},
  limitations: [
    'Page/context requests and WebSockets are recorded and restricted to the app origin; this is not host-wide packet capture or browser-process isolation.',
    'TLS/provider assertions come from the running backend receipts, not from a browser connection directly to the synthetic provider.',
    'Operations aborted before response headers have no browser request ID; their backend receipt is associated by a single scenario in an isolated observation interval.',
    'Run this script without another concurrent T06 client. Public authenticity, live providers, clinical validation, G05 and RAG remain outside this test.',
  ],
};
let browser;
let context;
let page;

function permittedDestination(raw, websocket = false) {
  const target = new URL(raw);
  return target.hostname === base.hostname && target.port === base.port
    && target.protocol === (websocket ? 'ws:' : 'http:');
}

async function backendReceipt(requestId) {
  assert.match(requestId, /^par02-[a-f0-9]{32}$/u);
  const filename = path.join(backendDirectory, `${requestId}.json`);
  const deadline = Date.now() + 8000;
  for (;;) {
    try {
      const bytes = await readFile(filename);
      const value = JSON.parse(bytes.toString('utf8'));
      await writeFile(path.join(output, 'backend-receipts', `${requestId}.json`), bytes);
      return { value, filename, sha256: createHash('sha256').update(bytes).digest('hex') };
    } catch (error) {
      if (error.code !== 'ENOENT' || Date.now() >= deadline) throw error;
      await pause(40); // Receipt publication follows response delivery and is atomic.
    }
  }
}

async function knownReceipts() {
  return new Set((await readdir(backendDirectory)).filter((name) => /^par02-[a-f0-9]{32}\.json$/u.test(name)));
}

async function receiptForAbortedScenario(scenario, known) {
  const deadline = Date.now() + 8000;
  for (;;) {
    const candidates = [];
    for (const name of await readdir(backendDirectory)) {
      if (!known.has(name) && /^par02-[a-f0-9]{32}\.json$/u.test(name)) {
        const value = JSON.parse(await readFile(path.join(backendDirectory, name), 'utf8'));
        if (value.scenario === scenario) candidates.push(value.request_id);
      }
    }
    assert.ok(candidates.length <= 1, `Ambiguous concurrent backend receipts for ${scenario}`);
    if (candidates.length === 1) return backendReceipt(candidates[0]);
    assert.ok(Date.now() < deadline, `No completed backend receipt for aborted ${scenario}`);
    await pause(40);
  }
}

async function awaitProviderRequest(scenario, known) {
  const deadline = Date.now() + 5000;
  for (;;) {
    const records = (await readFile(path.join(backendDirectory, 'events.jsonl'), 'utf8'))
      .split('\n').filter(Boolean).flatMap((line) => {
        try { return [JSON.parse(line)]; } catch { return []; } // Last append may be incomplete.
      });
    const matches = records.filter((item) => item.event === 'provider_tls_request'
      && item.scenario === scenario && !known.has(`${item.request_id}.json`));
    const ids = [...new Set(matches.map((item) => item.request_id))];
    assert.ok(ids.length <= 1, 'More than one T06 operation is active in the observed interval');
    if (ids.length === 1) return ids[0];
    assert.ok(Date.now() < deadline, `TLS provider was not reached for ${scenario}`);
    await pause(20);
  }
}

function verifyBackend(receipt, scenario, expectedStatus) {
  const value = receipt.value;
  assert.equal(value.scenario, scenario);
  assert.equal(value.http_status, expectedStatus);
  assert.equal(value.scope, 'synthetic_loopback_only');
  assert.equal(value.clinical_status, 'CLINICALLY_PENDING');
  assert.equal(value.provider_bind[0], '127.0.0.1');
  assert.ok(value.provider_requests >= 1, 'The real synthetic TLS provider must have received a request');
  assert.equal(value.tls_records.length, value.provider_requests);
  assert.equal(value.worker_stats.live, 0);
  assert.equal(value.worker_stats.unreaped, 0);
  assert.equal(value.runtime.pin_equivalence, true);
  for (const event of value.tls_records) {
    assert.equal(event.request_id, value.request_id);
    assert.equal(event.peer[0], '127.0.0.1');
    assert.equal(event.local[0], '127.0.0.1');
    assert.ok(['TLSv1.2', 'TLSv1.3'].includes(event.tls_version));
  }
  if (scenario === 'retry_429') assert.equal(value.provider_requests, 2);
  if (expectedStatus === 200) assert.equal(value.raw_hash_matches_transport, true);
  return {
    request_id: value.request_id, scenario: value.scenario, http_status: value.http_status,
    receipt_sha256: receipt.sha256, receipt: path.relative(output, path.join(output, 'backend-receipts', `${value.request_id}.json`)),
    provider_requests: value.provider_requests, tls_versions: [...new Set(value.tls_records.map((event) => event.tls_version))],
    worker_stats: value.worker_stats, runtime: value.runtime,
  };
}

const lab = () => page.locator('section[aria-label="Laboratorio T06"]');
const metadata = () => lab().locator('section[aria-label="Metadatos externos T06"]');
const status = () => lab().getByRole('status');
const receiptView = () => lab().locator('#receipt');

async function waitState(phase) {
  await status().filter({ hasText: states[phase] }).waitFor({ timeout: 10000 });
  assert.equal(await status().innerText(), states[phase]);
}

async function assertEmptyOutput() {
  assert.equal(await metadata().count(), 0);
  assert.equal(await receiptView().count(), 0);
}

async function enterFromHome() {
  await page.locator('a[href="/t06-lab"]').click();
  await page.waitForURL(`${base.origin}/t06-lab`);
  await lab().getByRole('heading', { name: 'Laboratorio T06 en localhost', exact: true }).waitFor();
  await waitState('idle');
}

async function runScenario(testCase) {
  const known = await knownReceipts();
  await lab().getByLabel('Caso sintético', { exact: true }).selectOption(testCase.id);
  await assertEmptyOutput();
  await lab().getByRole('button', { name: 'Ejecutar circuito', exact: true }).click();
  await waitState(testCase.phase);
  const ui = JSON.parse(await receiptView().innerText());
  assert.equal(ui.scenario, testCase.id);
  assert.equal(ui.expectedService, testCase.service);
  assert.equal(ui.phase, testCase.phase);
  assert.equal(ui.status, testCase.status);
  assert.equal(await metadata().locator('li').count(), testCase.rows);
  let receipt;
  let correlation;
  if (testCase.id === 'client_timeout') {
    assert.equal(ui.requestId, null);
    receipt = await receiptForAbortedScenario(testCase.id, known);
    correlation = 'unique scenario in isolated interval; browser aborted before headers';
    await waitState('timeout');
    assert.equal(await metadata().count(), 0);
    assert.deepEqual(JSON.parse(await receiptView().innerText()), ui, 'Late completion changed the timed-out UI');
  } else {
    assert.match(ui.requestId, /^par02-[a-f0-9]{32}$/u);
    assert.ok(network.some((event) => event.kind === 'response' && event.request_id === ui.requestId
      && event.status === testCase.status), 'The visible receipt ID must match a browser response');
    receipt = await backendReceipt(ui.requestId);
    correlation = 'browser response header = UI receipt = backend receipt';
  }
  const backend = verifyBackend(receipt, testCase.id, testCase.status ?? 200);
  assert.equal(await lab().locator('img, iframe, script, object, embed').count(), 0);
  assert.equal(await page.evaluate(() => globalThis.PAR02_XSS ?? null), null);
  if (testCase.phase === 'success') {
    assert.equal(await metadata().count(), 1);
    assert.equal(await lab().getByRole('alert').count(), 0);
    if (testCase.id === 'success') {
      const visible = await metadata().innerText();
      assert.ok(visible.includes('Niño, ação, 北京, 𝒜🩺'));
      assert.ok(visible.includes('<img src="https://external.example/pixel"'));
      assert.ok(visible.includes('<script>window.PAR02_XSS=2</script>'));
    }
    if (testCase.id === 'empty') await metadata().getByText('Sin registros.', { exact: true }).waitFor();
    if (testCase.id === 'long_text' || testCase.id === 'combined_limits') {
      const values = await metadata().locator('dd').allTextContents();
      const expected = testCase.id === 'long_text' ? '🩺'.repeat(1200) : '😀'.repeat(1800);
      assert.equal(values.filter((value) => value === expected).length, testCase.id === 'long_text' ? 1 : 50);
    }
    for (const link of await metadata().locator('a').all()) {
      assert.equal(await link.getAttribute('target'), '_blank');
      assert.equal(await link.getAttribute('rel'), 'noopener noreferrer');
      assert.equal(await link.getAttribute('referrerpolicy'), 'no-referrer');
    }
  } else {
    assert.equal(await metadata().count(), 0);
    const alert = await lab().getByRole('alert').innerText();
    assert.equal(alert, testCase.phase === 'rejected'
      ? 'Metadatos T06 rechazados. No se presenta contenido externo.'
      : testCase.phase === 'timeout'
        ? 'Tiempo de espera del navegador agotado. No se presenta contenido externo.'
        : 'La consulta de laboratorio ha fallado. No se presenta contenido externo.');
  }
  return { scenario: testCase.id, expected: testCase, ui, backend, correlation, result: 'PASS' };
}

async function beginPendingOperation() {
  const known = await knownReceipts();
  await lab().getByLabel('Caso sintético', { exact: true }).selectOption('timeout');
  await lab().getByRole('button', { name: 'Ejecutar circuito', exact: true }).click();
  await waitState('loading');
  // Wait for real provider activity before cancelling/navigating; no response is mocked or delayed here.
  const requestId = await awaitProviderRequest('timeout', known);
  return { known, requestId };
}

try {
  report.git = {
    head: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim(),
    working_tree_dirty: execFileSync('git', ['status', '--porcelain'], { cwd: root, encoding: 'utf8' }).trim().length > 0,
  };
  for (const filename of ['app/src/App.tsx', 'app/src/pages/Home.tsx', 'app/vite.config.ts',
    'app/src/t06/T06Lab.tsx', 'tools/t06-localhost-lab/lab/backend/server.py', 'app/scripts/check-t06-local-review.mjs']) {
    report.source_sha256[filename] = createHash('sha256').update(await readFile(path.join(root, filename))).digest('hex');
  }
  browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, headless: true,
    args: ['--no-sandbox', '--disable-background-networking', '--no-first-run'] });
  report.browser_version = browser.version();
  context = await browser.newContext({ viewport: { width: 1360, height: 1000 }, locale: 'es-ES',
    serviceWorkers: 'block', recordHar: { path: path.join(output, 'network.har'), content: 'omit', mode: 'minimal' } });
  await context.addInitScript(() => localStorage.setItem('emergency.lang', 'es'));
  await context.route('**/*', async (route) => {
    if (!permittedDestination(route.request().url())) {
      blockedDestinations.push({ kind: 'request', url: route.request().url() });
      await route.abort('blockedbyclient');
    } else await route.continue();
  });
  await context.routeWebSocket('**/*', (socket) => {
    const event = { kind: 'websocket', url: socket.url(), at_utc: new Date().toISOString() };
    network.push(event);
    if (!permittedDestination(socket.url(), true)) {
      blockedDestinations.push(event);
      socket.close({ code: 1008, reason: 'Only the local app is permitted' });
    } else socket.connectToServer();
  });
  context.on('request', (request) => network.push({ kind: 'request', url: request.url(), method: request.method(),
    resource_type: request.resourceType(), at_utc: new Date().toISOString() }));
  context.on('response', (response) => network.push({ kind: 'response', url: response.url(), status: response.status(),
    request_id: response.headers()['x-par02-request-id'] ?? null, at_utc: new Date().toISOString() }));
  context.on('requestfailed', (request) => network.push({ kind: 'requestfailed', url: request.url(),
    failure: request.failure()?.errorText ?? null, at_utc: new Date().toISOString() }));
  page = await context.newPage();
  page.setDefaultTimeout(10000);
  page.on('pageerror', (error) => pageErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push({ text: message.text(), location: message.location() });
  });
  await page.goto(base.href, { waitUntil: 'domcontentloaded' });
  assert.equal(await page.locator('meta[name="emergency-local-review"]').getAttribute('content'), 'synthetic-only');
  assert.equal(await page.locator('meta[name="emergency-local-platform"]').getAttribute('content'), 'linux');
  await enterFromHome();
  assert.deepEqual((await lab().locator('#scenario option').evaluateAll((options) => options.map((option) => option.value))).sort(),
    cases.map((item) => item.id).sort());
  for (const testCase of cases) {
    report.cases.push(await runScenario(testCase));
    console.log(`PASS T06 ${testCase.id}: ${testCase.phase}, HTTP ${testCase.status ?? 'aborted before headers'}`);
  }

  const cancelled = await beginPendingOperation();
  await lab().getByRole('button', { name: 'Cancelar', exact: true }).click();
  await waitState('cancelled');
  const cancelReceipt = await backendReceipt(cancelled.requestId);
  await waitState('cancelled');
  await assertEmptyOutput();
  report.state_checks.push({ check: 'explicit_cancel_after_tls_started', result: 'PASS',
    backend: verifyBackend(cancelReceipt, 'timeout', 504), correlation: 'provider event and isolated scenario interval; no UI response header' });

  const changed = await beginPendingOperation();
  await lab().getByLabel('Caso sintético', { exact: true }).selectOption('pubmed');
  await waitState('idle');
  const changeReceipt = await backendReceipt(changed.requestId);
  await waitState('idle');
  await assertEmptyOutput();
  assert.equal(await lab().getByLabel('Caso sintético', { exact: true }).inputValue(), 'pubmed');
  report.state_checks.push({ check: 'scenario_change_discards_completed_old_request', result: 'PASS',
    backend: verifyBackend(changeReceipt, 'timeout', 504), correlation: 'provider event and isolated scenario interval; no UI response header' });

  const left = await beginPendingOperation();
  await page.locator('header a[href="/"]').first().click();
  await page.waitForURL(base.href);
  await page.locator('#home-title').waitFor();
  const leftReceipt = await backendReceipt(left.requestId);
  assert.equal(await lab().count(), 0);
  await enterFromHome();
  await assertEmptyOutput();
  report.state_checks.push({ check: 'home_navigation_and_return_discard_old_request', result: 'PASS',
    backend: verifyBackend(leftReceipt, 'timeout', 504), correlation: 'provider event and isolated scenario interval; no UI response header' });

  report.state_checks.push({ check: 'recovery_after_errors_and_navigation', ...await runScenario(cases.find((item) => item.id === 'pubmed')) });
  await page.screenshot({ path: path.join(output, 'app-t06-pubmed.png'), fullPage: true });
  assert.equal(context.pages().length, 1, 'No provider link or popup should be opened');
  assert.deepEqual(blockedDestinations, [], 'The app attempted a request outside the local origin');
  assert.deepEqual(pageErrors, [], 'The composed app raised an uncaught browser error');
  assert.ok(network.every((event) => permittedDestination(event.url, event.kind === 'websocket')));
  report.verdict = 'PASS_LOCALHOST_EN_ALCANCE';
} catch (error) {
  report.verdict = 'FAIL';
  report.failure = { message: error.message, stack: error.stack };
  process.exitCode = 1;
} finally {
  await context?.close();
  await browser?.close();
  report.finished_utc = new Date().toISOString();
  report.distinct_scenarios = report.cases.length;
  report.state_observations = report.state_checks.length;
  report.page_errors = pageErrors;
  report.console_errors = consoleErrors;
  report.blocked_destinations = blockedDestinations;
  report.network_observations = network;
  report.network_origins = [...new Set(network.map((event) => new URL(event.url).origin))];
  await writeFile(path.join(output, 'RESULTS.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ verdict: report.verdict, scenarios: report.distinct_scenarios,
    state_checks: report.state_observations, report: path.join(output, 'RESULTS.json'), failure: report.failure?.message }));
}
