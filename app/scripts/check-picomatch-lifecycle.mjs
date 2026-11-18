import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const events = ['preinstall', 'install', 'postinstall', 'prepublish', 'preprepare', 'prepare', 'postprepare'];
const hash = text => createHash('sha256').update(text).digest('hex');
export function validateHooks(relative, scripts, reviewed) {
  const applicable = relative === '' ? events : ['preinstall', 'install', 'postinstall'];
  const actual = Object.fromEntries(applicable.filter(event => scripts[event]).map(event => [event, scripts[event]]));
  assert.deepEqual(actual, reviewed[relative] || {}, `Unreviewed lifecycle hooks: ${relative}`);
}
function preflight(root, config) {
  assert.ok(['win32', 'linux'].includes(process.platform), 'Full automatic lifecycle is reviewed for Windows/Linux only');
  const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
  assert.equal(hash(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8').replaceAll('\r\n', '\n')), config.lock_sha256);
  const reviewed = { '': { postinstall: 'node scripts/picomatch-mitigation.mjs --apply' }, 'node_modules/esbuild': { postinstall: 'node install.js' } };
  const metadata = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  assert.ok(!metadata.workspaces, 'Workspaces require separate lifecycle review');
  validateHooks('', metadata.scripts || {}, reviewed);
  for (const [relative, spec] of Object.entries(lock.packages)) {
    if (!relative) continue;
    assert.ok(!spec.resolved || spec.resolved.startsWith('https://registry.npmjs.org/'), `Unreviewed registry/source: ${relative}`);
    if (spec.hasInstallScript) assert.ok(['node_modules/esbuild', 'node_modules/fsevents'].includes(relative), `New installation script: ${relative}`);
    const directory = path.join(root, relative);
    if (!fs.existsSync(directory)) { assert.ok(spec.optional, `Missing required dependency: ${relative}`); continue; }
    assert.ok(!fs.lstatSync(directory).isSymbolicLink(), `Linked dependency: ${relative}`);
    const pkg = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8'));
    validateHooks(relative, pkg.scripts || {}, reviewed);
    assert.ok(!fs.existsSync(path.join(directory, 'binding.gyp')), `Unreviewed implicit node-gyp install: ${relative}`);
  }
  const esbuild = path.join(root, 'node_modules/esbuild');
  assert.equal(JSON.parse(fs.readFileSync(path.join(esbuild, 'package.json'), 'utf8')).version, config.lifecycle.esbuild.version);
  assert.equal(hash(fs.readFileSync(path.join(esbuild, 'install.js'))), config.lifecycle.esbuild.install_sha256, 'Unreviewed esbuild installer bytes');
  // fsevents is Darwin-only and must not run on the reviewed Windows/Linux matrix.
  assert.ok(!fs.existsSync(path.join(root, 'node_modules/fsevents')), 'Unexpected fsevents installation');
  return { reviewedRootHook: reviewed[''], reviewedDependencyHook: reviewed['node_modules/esbuild'], installerSha256: config.lifecycle.esbuild.install_sha256 };
}
function cleanEnvironment(directory) {
  const queried = spawnSync(process.execPath, [process.env.npm_execpath, 'config', 'get', 'cache', '--ignore-scripts'], { cwd: app, encoding: 'utf8', timeout: 10000 });
  assert.ifError(queried.error); assert.equal(queried.status, 0, 'Cannot identify the cache populated by the first installation');
  const cache = queried.stdout.trim();
  assert.ok(path.isAbsolute(cache) && !/[\r\n]/.test(cache), 'Expected one absolute npm cache path');
  assert.ok(fs.statSync(cache).isDirectory(), 'Expected an existing reviewed npm cache');
  const allowed = new Set(['PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'COMSPEC', 'HOME', 'USERPROFILE', 'LOCALAPPDATA', 'APPDATA']);
  const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => allowed.has(key.toUpperCase())));
  const empty = path.join(directory, 'empty.npmrc'); fs.writeFileSync(empty, '');
  return { ...env, npm_config_cache: cache, npm_config_userconfig: empty, npm_config_globalconfig: path.join(directory, 'empty-global.npmrc'), npm_config_registry: 'https://registry.npmjs.org/', npm_config_offline: 'true', npm_config_audit: 'false', npm_config_fund: 'false' };
}
function fullAutomaticLifecycle() {
  assert.ok(process.env.npm_execpath, 'Run through npm');
  const config = JSON.parse(fs.readFileSync(path.join(app, '../security/picomatch-mitigation.json'), 'utf8'));
  const review = preflight(app, config);
  const container = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-picomatch-full-ci-'));
  const root = path.join(container, 'app');
  const copy = relative => { const destination = path.resolve(root, relative); fs.mkdirSync(path.dirname(destination), { recursive: true }); fs.copyFileSync(path.resolve(app, relative), destination); };
  try {
    for (const file of ['package.json', 'package-lock.json', 'scripts/picomatch-mitigation.mjs', 'scripts/picomatch-runtime-policy.cjs', '../security/picomatch-mitigation.json']) copy(file);
    const env = cleanEnvironment(container);
    const args = [process.env.npm_execpath, 'ci', '--offline', '--foreground-scripts', '--no-audit', '--no-fund'];
    const child = spawnSync(process.execPath, args, { cwd: root, env, encoding: 'utf8', timeout: 240000, maxBuffer: 8 * 1024 * 1024 });
    assert.ifError(child.error); assert.equal(child.status, 0, child.stderr + child.stdout);
    assert.match(child.stdout, /> emergency@0\.1\.0 postinstall/);
    const check = spawnSync(process.execPath, ['scripts/picomatch-mitigation.mjs', '--check'], { cwd: root, env, encoding: 'utf8', timeout: 120000 });
    assert.ifError(check.error); assert.equal(check.status, 0, check.stderr);
    assert.equal(JSON.parse(check.stdout).copies.length, config.targets.length);
    assert.equal(hash(fs.readFileSync(path.join(root, 'package-lock.json'))), hash(fs.readFileSync(path.join(app, 'package-lock.json'))));
    // Revalidate installed hook bytes after npm verified cache integrity and ran them.
    preflight(root, config);
    console.log(JSON.stringify({ status: 'PASS', platform: process.platform, node: process.version, automaticFullInstall: true, projectHookObserved: true, thirdPartyHooks: ['esbuild@0.25.12:node install.js'], reviewed: review, packageLockUnchanged: true, guardedFiles: config.targets.length, scope: 'Exact full project package/lock and original postinstall files in an independent temporary install; no manually invoked hook; offline npm cache and no inherited credentials' }));
  } finally {
    assert.equal(path.dirname(container), os.tmpdir());
    assert.ok(path.basename(container).startsWith('emergency-picomatch-full-ci-'));
    fs.rmSync(container, { recursive: true, force: true });
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) fullAutomaticLifecycle();
