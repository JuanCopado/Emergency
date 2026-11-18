import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { test, after } from 'node:test';
import { runMode, hash } from './picomatch-mitigation.mjs';
import policy from './picomatch-runtime-policy.cjs';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const config = JSON.parse(fs.readFileSync(path.join(app, '../security/picomatch-mitigation.json'), 'utf8'));
const live = config.targets.map(t => [path.join(app, t.path), hash(fs.readFileSync(path.join(app, t.path)))]);
const require = createRequire(import.meta.url);
after(() => { for (const [file, digest] of live) assert.equal(hash(fs.readFileSync(file)), digest, 'Live dependencies changed during fixture tests'); });
function fixture(callback) {
  const container = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-picomatch-test-'));
  const root = path.join(container, 'emergency-picomatch-test-app');
  const copy = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); };
  for (const target of config.targets) {
    for (const relative of [target.path, `${target.package}/package.json`]) copy(path.join(app, relative), path.join(root, relative));
  }
  for (const relative of ['package-lock.json', 'scripts/picomatch-runtime-policy.cjs', '../security/picomatch-mitigation.json']) copy(path.join(app, relative), path.resolve(root, relative));
  fs.writeFileSync(path.join(root, '.picomatch-test-fixture'), 'synthetic test fixture');
  try { return callback(root); }
  finally {
    assert.equal(path.dirname(container), os.tmpdir());
    assert.ok(path.basename(container).startsWith('emergency-picomatch-test-'));
    fs.rmSync(container, { recursive: true, force: true });
  }
}
const target = root => path.join(root, config.targets[0].path);
const marker = root => path.join(root, 'node_modules/.emergency-picomatch-journal.json');
const locker = root => path.join(root, 'node_modules/.emergency-picomatch.lock');
function fault(method, substitute, callback) {
  const original = fs[method]; fs[method] = substitute(original);
  try { callback(); } finally { fs[method] = original; }
}

test('all reviewed standalone and embedded sources are guarded; tests preserve live bytes', () => {
  assert.equal(config.targets.length, 14);
  assert.equal(config.targets.filter(t => t.package === 'node_modules/rollup').reduce((sum, t) => sum + t.parsers, 0), 6);
  for (const [file, digest] of live) assert.equal(digest, config.targets.find(t => path.join(app, t.path) === file).patched_sha256);
});
test('fixture apply, check, idempotence and fixture-only revert', () => fixture(root => {
  assert.equal(runMode('--check', root).copies.length, config.targets.length);
  runMode('--revert', root); assert.throws(() => runMode('--check', root), /Guard absent/);
  assert.equal(hash(fs.readFileSync(target(root))), config.targets[0].original_sha256);
  runMode('--apply', root); runMode('--apply', root); runMode('--check', root);
  assert.throws(() => runMode('unexpected', root), /Use/);
}));
test('live revert and unknown source or policy bytes fail closed before mutation', () => {
  assert.throws(() => runMode('--revert', app), /private test fixtures/);
  fixture(root => { fs.appendFileSync(target(root), '// unknown'); assert.throws(() => runMode('--apply', root), /Unknown dependency bytes/); });
  fixture(root => { fs.appendFileSync(path.join(root, 'scripts/picomatch-runtime-policy.cjs'), '// unknown'); assert.throws(() => runMode('--apply', root), /Unknown runtime policy/); });
});
test('locked identity, package version, missing copies and unexpected embedded sources fail closed', () => {
  fixture(root => { fs.appendFileSync(path.join(root, 'package-lock.json'), ' '); assert.throws(() => runMode('--apply', root), /Unreviewed package-lock/); });
  fixture(root => { const file = path.join(root, config.targets[0].package, 'package.json'); const data = JSON.parse(fs.readFileSync(file)); data.version = '999.0.0'; fs.writeFileSync(file, JSON.stringify(data)); assert.throws(() => runMode('--apply', root), /Unreviewed package version/); });
  fixture(root => { fs.renameSync(path.join(root, 'node_modules/picomatch'), path.join(root, 'node_modules/moved')); assert.throws(() => runMode('--apply', root), /inventory differs|Unreviewed embedded parser/); });
  fixture(root => { fs.writeFileSync(path.join(root, 'node_modules/unknown.js'), 'const extglobOpen = (type, value) => {};'); assert.throws(() => runMode('--apply', root), /Unreviewed embedded parser/); });
});
test('links are rejected without following them', () => fixture(root => {
  const destination = path.join(root, 'node_modules/linked');
  fs.symlinkSync(path.join(root, 'node_modules/picomatch'), destination, process.platform === 'win32' ? 'junction' : 'dir');
  assert.throws(() => runMode('--apply', root), /Linked dependency/);
}));
test('atomic replacement failure leaves complete known files and blocks check until forward recovery', () => fixture(root => {
  runMode('--revert', root); let count = 0;
  fault('renameSync', original => (...args) => { if (++count === 3) throw new Error('synthetic interrupted replacement'); return original(...args); }, () => assert.throws(() => runMode('--apply', root), /synthetic interrupted/));
  assert.ok(fs.existsSync(marker(root)));
  for (const spec of config.targets) assert.ok([spec.original_sha256, spec.patched_sha256].includes(hash(fs.readFileSync(path.join(root, spec.path)))));
  assert.throws(() => runMode('--check', root), /Pending/);
  assert.throws(() => runMode('--revert', root), /forward recovery/);
  runMode('--apply', root); runMode('--check', root); assert.ok(!fs.existsSync(marker(root)));
  assert.ok(!fs.readdirSync(path.dirname(target(root))).some(name => name.endsWith('.tmp')));
}));
test('write verification and unknown pending transactions fail closed', () => {
  fixture(root => {
    runMode('--revert', root);
    fault('renameSync', original => (...args) => { original(...args); fs.appendFileSync(args[1], '// synthetic corruption'); }, () => assert.throws(() => runMode('--apply', root), /verification failed/));
    assert.throws(() => runMode('--check', root), /Pending/);
    assert.throws(() => runMode('--apply', root), /Unknown dependency bytes/);
  });
  fixture(root => { fs.writeFileSync(marker(root), '{}'); assert.throws(() => runMode('--apply', root), /Unknown pending transaction/); });
});
test('exclusive lock refuses a live owner and recovers a dead owner', () => fixture(root => {
  fs.writeFileSync(locker(root), JSON.stringify({ pid: process.pid, token: 'synthetic' }));
  assert.throws(() => runMode('--apply', root), /Another installer/); assert.throws(() => runMode('--check', root), /Pending/);
  fs.writeFileSync(locker(root), '{}'); assert.throws(() => runMode('--apply', root), /Invalid installer lock/);
  const child = spawnSync(process.execPath, ['-e', 'process.exit(0)'], { timeout: 3000 }); assert.equal(child.status, 0);
  // Node's completed child PID is known dead; no guessed system PID is signalled.
  fs.writeFileSync(locker(root), JSON.stringify({ pid: child.pid, token: 'dead-synthetic' }));
  runMode('--apply', root); runMode('--check', root);
}));
test('safe repeated literals/classes/prefix-free alternatives retain their semantics', () => {
  const patterns = [['a+(b)', 'abbb'], ['*([0-9]).txt', '123.txt'], ['+([a-z]).js', 'abc.js'], ['x/*(a)/y', 'x/aaa/y'], ['+(ab|ac)', 'abac']];
  for (const relative of [...new Set(config.targets.filter(t => t.package.endsWith('/picomatch')).map(t => t.package))]) {
    const pm = require(path.join(app, relative));
    for (const [pattern, input] of patterns) assert.equal(pm(pattern)(input), true, `${relative} ${pattern}`);
  }
  policy.assertRepeated('+(a|b)', 0); policy.assertRepeated('+(a|A)', 0);
  assert.throws(() => policy.assertRepeated('+(a|A)', 0, { nocase: true }), /prefix-free/);
  assert.throws(() => policy.assertRepeated('+(a|A)', 0, { flags: 'i' }), /prefix-free/);
});
test('policy rejects ambiguous, nested and unreviewed repetitions without running a regex', () => {
  for (const pattern of ['+(*a)', '*(*)', '+(a|aa)', '+()', '+(a\\b)', '+("a")', '+((a))', '+([[a]])', '+(a']) assert.throws(() => policy.assertRepeated(pattern, 0), /Temporary picomatch/);
  for (const options of [{ prepend: '(a+)+b' }, { expandRange() {} }]) assert.throws(() => policy.validatePatternOptions('a', options), /regex injection/);
  assert.throws(() => policy.validatePatternOptions('a'.repeat(1025)), /length/);
  assert.throws(() => policy.validatePatternOptions(null), /type/);
  assert.equal(policy.validatePatternOptions('a', { regex: true }).regex, false);
});
test('runtime budget rejects polynomial workloads before execution and preserves ordinary RegExp behavior', () => {
  assert.deepEqual(policy.complexity('"*"\\*[*]**/?(a|b),!(x)+([ab])'), { variable: 3, choices: 4 });
  const regex = policy.guardRegex(/^a$/, 'a'); assert.ok(regex instanceof RegExp); assert.equal(regex.test('a'), true); assert.equal(regex.exec('b'), null);
  assert.throws(() => regex.exec('x'.repeat(8193)), /length/); assert.throws(() => regex.exec(123), /non-string/);
  assert.throws(() => policy.assertWork('*a'.repeat(9) + '*b', 'a'.repeat(36) + '!', { variable: 10, choices: 1 }), /work budget/);
  assert.throws(() => policy.complexity('?('.repeat(30)), /branch budget/);
});
