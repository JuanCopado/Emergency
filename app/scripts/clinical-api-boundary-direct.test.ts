// @vitest-environment node
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { request } from 'node:http';
import { fileURLToPath } from 'node:url';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { createServer, type ViteDevServer } from 'vite';
import { clinicalApiBoundary, clinicalApiProxy } from './clinical-api-boundary.mjs';

const uiPort = 4221;
const unconfiguredPort = 4222;
const origin = `http://127.0.0.1:${uiPort}`;
const token = randomBytes(32).toString('hex');
let backend: ChildProcessWithoutNullStreams;
let server: ViteDevServer;
let unconfigured: ViteDevServer;

function call(port: number, headers: string[], method = 'POST', path = '/api/clinical-note/new') {
  return new Promise<{ status: number; body: string; cache: string | undefined }>((resolve, reject) => {
    const req = request({ hostname: '127.0.0.1', port, path, method, headers: [
      ...headers, ...(method === 'POST' ? ['Content-Type', 'application/json', 'Content-Length', '2'] : []),
    ] }, response => {
      let body = '';
      response.on('data', chunk => { body += chunk; });
      response.on('end', () => resolve({ status: response.statusCode!, body, cache: response.headers['cache-control'] }));
    });
    req.setTimeout(3000, () => req.destroy(new Error('Synthetic local API request timed out')));
    req.on('error', reject);
    req.end(method === 'POST' ? '{}' : undefined);
  });
}

beforeAll(async () => {
  backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
    `import os; from clinical_note_api import make_server; s=make_server(ui_port=${uiPort},session_token=os.environ['EMERGENCY_LOCAL_API_TOKEN']); print(s.server_port,flush=True); s.serve_forever()`,
  ], { cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)),
    env: { ...process.env, EMERGENCY_LOCAL_API_TOKEN: token }, stdio: 'pipe' });
  const backendPort = await new Promise<number>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Synthetic API startup timeout')), 10000);
    let output = '';
    backend.stdout.on('data', chunk => {
      output += chunk;
      if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); }
    });
    backend.on('error', error => { clearTimeout(timeout); reject(error); });
    backend.on('exit', code => { clearTimeout(timeout); reject(new Error(`Synthetic API exited ${code}`)); });
  });
  const proxy = Object.fromEntries(['clinical-note', 'pediatric-outpatient', 'clinical-scores', 'acute-medications']
    .map(family => [`/api/${family}`, clinicalApiProxy(`http://127.0.0.1:${backendPort}`, token)]));
  // Direct imports keep this exact middleware under Vitest's instrumentation.
  // The existing companion suite separately verifies the product's real Vite configuration.
  server = await createServer({ configFile: false, logLevel: 'silent', plugins: [clinicalApiBoundary(token)],
    server: { host: '127.0.0.1', port: uiPort, strictPort: true, proxy } });
  await server.listen();
  unconfigured = await createServer({ configFile: false, logLevel: 'silent', plugins: [clinicalApiBoundary('')],
    server: { host: '127.0.0.1', port: unconfiguredPort, strictPort: true, proxy } });
  await unconfigured.listen();
}, 15000);

afterAll(async () => {
  await Promise.all([server?.close(), unconfigured?.close()]);
  if (backend && backend.exitCode === null) {
    const exited = new Promise<void>(resolve => backend.once('exit', () => resolve()));
    backend.kill();
    await exited;
  }
});

describe('directly imported middleware with a real local proxy and backend', () => {
  const trusted = ['Host', `127.0.0.1:${uiPort}`, 'Origin', origin];

  it('forwards all API families after validation and replaces the browser credential', async () => {
    for (const [path, status] of [
      ['/api/clinical-note/new', 200], ['/api/clinical-scores/catalog', 200],
      ['/api/acute-medications/catalog', 200], ['/api/pediatric-outpatient/calculate', 422],
    ] as const) {
      const response = await call(uiPort, [...trusted, 'X-Emergency-Local-Token', 'browser-value'], 'POST', path);
      expect(response.status, path).toBe(status);
      expect(response.cache).toBe('no-store');
      expect(response.body).not.toContain(token);
    }
  });

  it('rejects invalid, missing and duplicate origin metadata before proxying', async () => {
    const cases = [
      ['Host', 'attacker.invalid', 'Origin', origin],
      ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'http://localhost.attacker.invalid'],
      ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'null'],
      ['Host', `127.0.0.1:${uiPort}`],
      [...trusted, 'Origin', origin], [...trusted, 'Host', `127.0.0.1:${uiPort}`],
      [...trusted, 'Sec-Fetch-Site', 'cross-site'],
      [...trusted, 'Sec-Fetch-Site', 'same-origin', 'Sec-Fetch-Site', 'same-origin'],
      ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'https://attacker.invalid',
        'X-Forwarded-Host', `127.0.0.1:${uiPort}`, 'X-Forwarded-For', '127.0.0.1', 'X-Emergency-Local-Token', token],
    ];
    for (const headers of cases) {
      const response = await call(uiPort, headers);
      expect(response.status).toBe(403);
      expect(response.cache).toBe('no-store');
      expect(JSON.parse(response.body)).toEqual({ error: 'Local request origin is not permitted.' });
    }
    expect((await call(uiPort, cases[0], 'POST', '/api/clinical-note-extra')).status).toBe(403);
  });

  it('allows minimal local health but rejects foreign health origins and leaves unrelated routes alone', async () => {
    const response = await call(uiPort, ['Host', `127.0.0.1:${uiPort}`], 'GET', '/api/clinical-note/health');
    expect(response.status).toBe(200);
    expect(JSON.parse(response.body)).toEqual({ status: 'ok', api_version: '1.0' });
    expect((await call(uiPort, ['Host', 'attacker.invalid'], 'GET', '/api/clinical-note/health')).status).toBe(403);
    expect((await call(uiPort, ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'https://attacker.invalid'], 'GET', '/api/clinical-note/health')).status).toBe(403);
    const unrelated = await call(uiPort, ['Host', `127.0.0.1:${uiPort}`, 'Accept', 'application/json'], 'GET', '/unrelated-synthetic-route');
    expect(unrelated.status).toBe(404);
  });

  it('fails closed without a configured process session even if the caller presents a valid credential', async () => {
    const response = await call(unconfiguredPort, [
      'Host', `127.0.0.1:${unconfiguredPort}`, 'Origin', `http://127.0.0.1:${unconfiguredPort}`,
      'X-Emergency-Local-Token', token,
    ]);
    expect(response.status).toBe(503);
    expect(response.cache).toBe('no-store');
    expect(JSON.parse(response.body)).toEqual({ error: 'Local API session is not configured.' });
    expect(response.body).not.toContain(token);
  });
});
