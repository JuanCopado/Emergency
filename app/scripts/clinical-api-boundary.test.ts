// @vitest-environment node
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { mkdtemp, rm } from 'node:fs/promises';
import { request } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { createServer, preview, type PreviewServer, type ViteDevServer } from 'vite';
import { clinicalApiProxy } from './clinical-api-boundary.mjs';

const uiPort = 4219;
const origin = `http://127.0.0.1:${uiPort}`;
const token = randomBytes(32).toString('hex');
const originalToken = process.env.EMERGENCY_LOCAL_API_TOKEN;
const configFile = fileURLToPath(new URL('../vite.config.ts', import.meta.url));
let backend: ChildProcessWithoutNullStreams;
let backendPort: number;
let server: ViteDevServer;

function localProxies() {
  return Object.fromEntries(['clinical-note', 'pediatric-outpatient', 'clinical-scores', 'acute-medications']
    .map(family => [`/api/${family}`, clinicalApiProxy(`http://127.0.0.1:${backendPort}`, token)]));
}

function call(port: number, headers: string[], method = 'POST', path = '/api/clinical-note/new') {
  return new Promise<{ status: number; body: string }>((resolve, reject) => {
    const req = request({ hostname: '127.0.0.1', port, path, method, headers: [
      ...headers, ...(method === 'POST' ? ['Content-Type', 'application/json', 'Content-Length', '2'] : []),
    ] }, response => {
      let body = '';
      response.on('data', chunk => { body += chunk; });
      response.on('end', () => resolve({ status: response.statusCode!, body }));
    });
    req.setTimeout(3000, () => req.destroy(new Error('Synthetic local API request timed out')));
    req.on('error', reject);
    req.end(method === 'POST' ? '{}' : undefined);
  });
}

beforeAll(async () => {
  process.env.EMERGENCY_LOCAL_API_TOKEN = token;
  backend = spawn(process.env.CLINICAL_QA_PYTHON || 'python', ['-B', '-u', '-c',
    `import os; from clinical_note_api import make_server; s=make_server(ui_port=${uiPort},session_token=os.environ['EMERGENCY_LOCAL_API_TOKEN']); print(s.server_port,flush=True); s.serve_forever()`,
  ], { cwd: fileURLToPath(new URL('../../clinical/scripts/', import.meta.url)),
    env: { ...process.env, EMERGENCY_LOCAL_API_TOKEN: token }, stdio: 'pipe' });
  backendPort = await new Promise<number>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Synthetic API startup timeout')), 10000);
    let output = '';
    backend.stdout.on('data', chunk => {
      output += chunk;
      if (/^\d+\r?\n/.test(output)) { clearTimeout(timeout); resolve(Number(output.trim())); }
    });
    backend.on('error', error => { clearTimeout(timeout); reject(error); });
    backend.on('exit', code => { clearTimeout(timeout); reject(new Error(`Synthetic API exited ${code}`)); });
  });
  // Load the application's configuration; only the synthetic backend destination changes.
  server = await createServer({ configFile, logLevel: 'silent',
    server: { host: '127.0.0.1', port: uiPort, strictPort: true, proxy: localProxies() } });
  await server.listen();
}, 15000);

afterAll(async () => {
  await server?.close();
  if (originalToken === undefined) delete process.env.EMERGENCY_LOCAL_API_TOKEN;
  else process.env.EMERGENCY_LOCAL_API_TOKEN = originalToken;
  if (backend && backend.exitCode === null) {
    const exited = new Promise<void>(resolve => backend.once('exit', () => resolve()));
    backend.kill();
    await exited;
  }
});

describe('real local Vite proxy and clinical backend boundary', () => {
  const trusted = ['Host', `127.0.0.1:${uiPort}`, 'Origin', origin];

  it('serves the existing contract without exposing a credential to the browser', async () => {
    const response = await call(uiPort, trusted);
    expect(response.status).toBe(200);
    expect(JSON.parse(response.body).schema_version).toBe('1.0');
    expect(response.body).not.toContain(token);
  });

  it('overwrites a browser-supplied credential only after checking the request origin', async () => {
    expect((await call(uiPort, [...trusted, 'X-Emergency-Local-Token', 'untrusted-client-token'])).status).toBe(200);
    const foreign = ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'https://attacker.invalid',
      'X-Emergency-Local-Token', token, 'X-Forwarded-Host', `127.0.0.1:${uiPort}`, 'X-Forwarded-For', '127.0.0.1'];
    expect((await call(uiPort, foreign)).status).toBe(403);
  });

  it('rejects foreign, absent and duplicate browser metadata at the proxy', async () => {
    const cases = [
      ['Host', 'attacker.invalid', 'Origin', origin],
      ['Host', `127.0.0.1:${uiPort}`],
      ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'null'],
      [...trusted, 'Origin', origin], [...trusted, 'Host', `127.0.0.1:${uiPort}`],
      [...trusted, 'Sec-Fetch-Site', 'cross-site'],
      [...trusted, 'Sec-Fetch-Site', 'same-origin', 'Sec-Fetch-Site', 'same-origin'],
    ];
    for (const headers of cases) expect((await call(uiPort, headers)).status).toBe(403);
  });

  it('rejects direct backend calls without the private process credential', async () => {
    const direct = ['Host', `127.0.0.1:${backendPort}`, 'Origin', origin];
    expect((await call(backendPort, direct)).status).toBe(401);
    expect((await call(backendPort, [...direct, 'X-Emergency-Local-Token', token])).status).toBe(200);
  });

  it('keeps health checks minimal and never issues a session credential', async () => {
    const response = await call(uiPort, ['Host', `127.0.0.1:${uiPort}`], 'GET', '/api/clinical-note/health');
    expect(response.status).toBe(200);
    expect(JSON.parse(response.body)).toEqual({ status: 'ok', api_version: '1.0' });
  });

  it('refuses remote, credential-bearing and path-bearing proxy destinations', () => {
    for (const target of ['https://example.test', 'http://localhost:8765', 'http://127.0.0.1:8765/path',
      'http://user:secret@127.0.0.1:8765', 'http://127.0.0.1:8765/?query=1']) {
      expect(() => clinicalApiProxy(target, token)).toThrow('direct IPv4 loopback origin');
    }
  });

  it('preserves the same boundary and all existing API families in the real preview configuration', async () => {
    await server.close();
    // CI runs unit tests before building. API proxy checks need only an empty output directory.
    const output = await mkdtemp(join(tmpdir(), 'emergency-http-preview-'));
    let previewServer: PreviewServer | undefined;
    try {
      previewServer = await preview({ configFile, logLevel: 'silent', build: { outDir: output },
        preview: { host: '127.0.0.1', port: uiPort, strictPort: true, proxy: localProxies() } });
      for (const [path, status] of [
        ['/api/clinical-note/new', 200], ['/api/clinical-scores/catalog', 200],
        ['/api/acute-medications/catalog', 200], ['/api/pediatric-outpatient/calculate', 422],
      ] as const) {
        const response = await call(uiPort, trusted, 'POST', path);
        expect(response.status, path).toBe(status);
        expect(response.body).not.toContain(token);
      }
      expect((await call(uiPort, ['Host', `127.0.0.1:${uiPort}`, 'Origin', 'null'])).status).toBe(403);
      expect((await call(uiPort, ['Host', 'attacker.invalid'], 'GET', '/api/clinical-note/health')).status).toBe(403);
      const health = await call(uiPort, ['Host', `127.0.0.1:${uiPort}`], 'GET', '/api/clinical-note/health');
      expect(health.status).toBe(200);
      expect(JSON.parse(health.body)).toEqual({ status: 'ok', api_version: '1.0' });
    } finally {
      try {
        if (previewServer) await new Promise<void>((resolve, reject) => previewServer.httpServer.close(error => error ? reject(error) : resolve()));
      } finally {
        await rm(output, { recursive: true, force: true });
      }
    }
  });
});
