import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const value = flag => { const index = args.indexOf(flag); return index < 0 ? undefined : args[index + 1]; };
const mode = value('--mode');
const output = value('--output');
assert.ok(['postinstall', 'ignore-scripts'].includes(mode), 'Use --mode postinstall or --mode ignore-scripts');
assert.equal(args.length, output ? 4 : 2, 'Unexpected installation-check arguments');
assert.ok(process.env.npm_execpath, 'Run through npm run security:picomatch:installation-check');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const lockPath = path.join(app, 'package-lock.json');
const lockHash = hash(fs.readFileSync(lockPath));
const steps = [];
function run(label, argv, expected, requiredError) {
  const result = spawnSync(process.execPath, argv, { cwd: app, encoding: 'utf8', timeout: 30000 });
  assert.ifError(result.error);
  assert.equal(result.status, expected, `${label}: ${result.stderr || result.stdout}`);
  if (requiredError) assert.match(result.stderr + result.stdout, requiredError);
  steps.push({ label, exitCode: result.status, expectedExitCode: expected });
  return result;
}
const controller = path.join(app, 'scripts/picomatch-mitigation.mjs');
if (mode === 'ignore-scripts') {
  run('clean install without lifecycle scripts is unguarded', [controller, '--check'], 1, /Guard absent/);
  run('prebuild refuses unguarded dependencies', [process.env.npm_execpath, 'run', 'prebuild'], 1, /Guard absent/);
  run('explicit apply', [controller, '--apply'], 0);
} else run('postinstall applied the guard automatically', [controller, '--check'], 0);
run('application is idempotent', [controller, '--apply'], 0);
const final = run('all installed copies are guarded', [controller, '--check'], 0);
const state = JSON.parse(final.stdout);
assert.equal(state.copies.length, 5, 'Expected all five locked picomatch copies');
assert.equal(hash(fs.readFileSync(lockPath)), lockHash, 'package-lock changed');
const report = { observedUTC: new Date().toISOString(), status: 'PASS', mode, platform: process.platform, arch: process.arch, node: process.version, lockSha256: lockHash, packageLockUnchanged: true, steps, guardedCopies: state.copies, trivyPolicy: 'Unchanged: advisory and blocking gate remain applicable.' };
if (output) fs.writeFileSync(path.resolve(output), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify(report, null, 2));
