import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

// A real automatic npm root lifecycle, in a dependency-free synthetic package.
// Third-party dependency scripts are intentionally never enabled by this test.
const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
assert.ok(process.env.npm_execpath, 'Run through npm');
const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-picomatch-lifecycle-'));
const nonce = randomUUID();
try {
  const controller = path.join(app, 'scripts/picomatch-mitigation.mjs');
  const hook = `import {spawnSync} from 'node:child_process';import fs from 'node:fs';import assert from 'node:assert/strict';assert.equal(process.env.npm_lifecycle_event,'postinstall');const r=spawnSync(process.execPath,${JSON.stringify([controller, '--apply'])},{stdio:'inherit'});assert.equal(r.status,0);fs.writeFileSync('proof.json',JSON.stringify({nonce:${JSON.stringify(nonce)},event:process.env.npm_lifecycle_event}));`;
  fs.writeFileSync(path.join(directory, 'hook.mjs'), hook);
  const metadata = { name: 'synthetic-lifecycle-test', version: '1.0.0', private: true, scripts: { postinstall: 'node hook.mjs' } };
  fs.writeFileSync(path.join(directory, 'package.json'), JSON.stringify(metadata));
  fs.writeFileSync(path.join(directory, 'package-lock.json'), JSON.stringify({ name: metadata.name, version: metadata.version, lockfileVersion: 3, requires: true, packages: { '': { name: metadata.name, version: metadata.version, hasInstallScript: true } } }));
  const child = spawnSync(process.execPath, [process.env.npm_execpath, 'ci', '--offline', '--no-audit', '--no-fund'], { cwd: directory, encoding: 'utf8', timeout: 180000 });
  assert.ifError(child.error); assert.equal(child.status, 0, child.stderr + child.stdout);
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(directory, 'proof.json'))), { nonce, event: 'postinstall' });
  console.log(JSON.stringify({ status: 'PASS', platform: process.platform, automaticRootLifecycle: true, thirdPartyLifecycles: false, scope: 'Dependency-free npm fixture invokes the exact reviewed project postinstall controller' }));
} finally {
  assert.equal(path.dirname(directory), os.tmpdir());
  assert.ok(path.basename(directory).startsWith('emergency-picomatch-lifecycle-'));
  fs.rmSync(directory, { recursive: true, force: true });
}
