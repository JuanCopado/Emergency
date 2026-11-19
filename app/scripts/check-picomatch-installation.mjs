import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const value = flag => { const index = args.indexOf(flag); return index < 0 ? undefined : args[index + 1]; };
const requestedMode = value('--mode');
const mode = ({ postinstall: 'project-hook', 'ignore-scripts': 'explicit-apply' })[requestedMode] || requestedMode;
const output = value('--output');
assert.ok(['project-hook', 'explicit-apply', 'automatic-full'].includes(mode), 'Use --mode project-hook, explicit-apply or automatic-full');
assert.equal(args.length, output ? 4 : 2, 'Unexpected installation-check arguments');
assert.ok(process.env.npm_execpath, 'Run through npm run security:picomatch:installation-check');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const lockPath = path.join(app, 'package-lock.json');
const lockHash = hash(fs.readFileSync(lockPath));
const steps = [];
let automaticLifecycle;
function run(label, argv, expected, requiredError) {
  const result = spawnSync(process.execPath, argv, { cwd: app, encoding: 'utf8', timeout: 480000 });
  assert.ifError(result.error);
  assert.equal(result.status, expected, `${label}: ${result.stderr || result.stdout}`);
  if (requiredError) assert.match(result.stderr + result.stdout, requiredError);
  steps.push({ label, exitCode: result.status, expectedExitCode: expected });
  return result;
}
const controller = path.join(app, 'scripts/picomatch-mitigation.mjs');
if (mode === 'explicit-apply') {
  run('clean install without lifecycle scripts is unguarded', [controller, '--check'], 1, /Guard absent/);
  const scripts = JSON.parse(fs.readFileSync(path.join(app, 'package.json'), 'utf8')).scripts;
  for (const name of Object.keys(scripts).filter(name => !(name.startsWith('pre') && Object.hasOwn(scripts, name.slice(3))) && name !== 'postinstall' && !name.startsWith('security:'))) {
    const hook = `pre${name}`;
    assert.equal(scripts[hook], 'node scripts/picomatch-mitigation.mjs --check', `Missing guard for ${name}`);
    run(`${hook} refuses unguarded dependencies`, [process.env.npm_execpath, 'run', hook], 1, /Guard absent/);
  }
  run('explicit apply', [controller, '--apply'], 0);
} else {
  if (mode === 'automatic-full') automaticLifecycle = JSON.parse(run('automatic full npm installation with reviewed dependency hooks', [path.join(app, 'scripts/check-picomatch-lifecycle.mjs')], 0).stdout);
  if (mode === 'automatic-full') run('explicit apply to working dependencies after independent automatic install proof', [controller, '--apply'], 0);
  run('project postinstall applied the guard', [controller, '--check'], 0);
}
run('application is idempotent', [controller, '--apply'], 0);
const final = run('all installed copies are guarded', [controller, '--check'], 0);
const state = JSON.parse(final.stdout);
const config = JSON.parse(fs.readFileSync(path.join(app, '../security/picomatch-mitigation.json'), 'utf8'));
assert.equal(state.copies.length, config.targets.length, 'Every reviewed standalone and embedded file must be guarded');
assert.equal(hash(fs.readFileSync(lockPath)), lockHash, 'package-lock changed');
const report = { observedUTC: new Date().toISOString(), status: 'PASS', mode, automaticLifecycle, platform: process.platform, arch: process.arch, node: process.version, lockSha256: lockHash, packageLockUnchanged: true, steps, guardedCopies: state.copies, trivyPolicy: 'Unchanged gate; all current scanner findings stay visible.' };
if (output) fs.writeFileSync(path.resolve(output), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(report, null, 2));
