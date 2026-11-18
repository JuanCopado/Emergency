import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const fail = message => { throw new Error(message); };
const slash = value => value.split(path.sep).join('/');
function ordinary(target, directory = false) {
  const stat = fs.lstatSync(target);
  if (stat.isSymbolicLink() || (directory ? !stat.isDirectory() : !stat.isFile())) fail(`Expected ordinary path: ${target}`);
}
function fixtureOnly(root) {
  const relative = path.relative(os.tmpdir(), root);
  if (relative.startsWith('..') || path.isAbsolute(relative) || !path.basename(root).startsWith('emergency-picomatch-test-')) fail('Revert is restricted to private test fixtures');
  ordinary(path.join(root, '.picomatch-test-fixture'));
}
function readConfig(root) {
  const modules = path.join(root, 'node_modules');
  ordinary(modules, true);
  if (path.resolve(fs.realpathSync(modules)) !== path.resolve(modules)) fail('Linked node_modules is not supported');
  const config = JSON.parse(fs.readFileSync(path.join(root, '../security/picomatch-mitigation.json'), 'utf8'));
  const lockText = fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8').replaceAll('\r\n', '\n');
  if (hash(lockText) !== config.lock_sha256) fail('Unreviewed package-lock');
  const policy = path.join(root, 'scripts/picomatch-runtime-policy.cjs');
  ordinary(policy);
  if (hash(fs.readFileSync(policy, 'utf8').replaceAll('\r\n', '\n')) !== config.policy_sha256) fail('Unknown runtime policy bytes');
  const lock = JSON.parse(lockText);
  const expectedPackages = Object.keys(lock.packages).filter(p => /\/picomatch$/.test(p) || p === 'node_modules/rollup').sort();
  const reviewedPackages = [...new Set(config.targets.map(t => t.package))].sort();
  if (JSON.stringify(expectedPackages) !== JSON.stringify(reviewedPackages)) fail('Unreviewed locked package inventory');
  return { config, modules, expectedPackages };
}
function checkEmbeddedFile(filename, root, known) {
  if (!/\.(?:[cm]?js)$/.test(filename)) return;
  const relative = slash(path.relative(root, filename));
  if (known.has(relative)) return;
  const text = fs.readFileSync(filename, 'utf8');
  if (/const extglobOpen\s*=\s*\(type, value\)/.test(text) || /function analyzeRepeatedExtglob\(/.test(text)) fail(`Unreviewed embedded parser: ${relative}`);
}
function scanInstalled(root, modules, known) {
  const actualPackages = [];
  function walk(directory) {
    ordinary(directory, true);
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === '.bin') continue; // npm launchers, not package source
      const filename = path.join(directory, entry.name);
      if (entry.isSymbolicLink()) fail(`Linked dependency: ${filename}`);
      if (entry.isDirectory()) {
        if (['picomatch', 'rollup'].includes(entry.name)) actualPackages.push(slash(path.relative(root, filename)));
        walk(filename);
      } else if (entry.isFile()) checkEmbeddedFile(filename, root, known);
    }
  }
  walk(modules);
  return actualPackages.sort();
}
function transformed(text, spec, reverse) {
  if (reverse) {
    if (!text.startsWith(spec.header)) fail('Missing policy binding');
    text = text.slice(spec.header.length);
  }
  const replacements = reverse ? [...spec.replacements].reverse() : spec.replacements;
  for (const [original, patched, count] of replacements) {
    const anchor = reverse ? patched : original, replacement = reverse ? original : patched;
    if (text.split(anchor).length - 1 !== count) fail(`Ambiguous parser anchor: ${spec.path}`);
    text = text.replaceAll(anchor, replacement);
  }
  return reverse ? text : spec.header + text;
}
function planFile(root, modules, spec, mode) {
  const target = path.join(root, spec.path);
  let directory = path.dirname(target);
  while (directory !== modules) { ordinary(directory, true); directory = path.dirname(directory); }
  ordinary(target);
  const metadata = JSON.parse(fs.readFileSync(path.join(root, spec.package, 'package.json'), 'utf8'));
  if (metadata.version !== spec.version) fail(`Unreviewed package version: ${spec.package}`);
  const before = fs.readFileSync(target), digest = hash(before);
  if (![spec.original_sha256, spec.patched_sha256].includes(digest)) fail(`Unknown dependency bytes: ${spec.path}`);
  const patched = digest === spec.patched_sha256;
  if (mode === '--check' && !patched) fail(`Guard absent: ${spec.path}`);
  let text = before.toString('utf8');
  if (mode === '--apply' && !patched) text = transformed(text, spec, false);
  if (mode === '--revert' && patched) text = transformed(text, spec, true);
  const after = Buffer.from(text);
  const expected = mode === '--revert' ? spec.original_sha256 : spec.patched_sha256;
  if (hash(after) !== expected) fail(`Unexpected planned digest: ${spec.path}`);
  return { ...spec, target, before, after };
}
function loadPlan(root, mode) {
  const { config, modules, expectedPackages } = readConfig(root);
  const actualPackages = scanInstalled(root, modules, new Set(config.targets.map(t => t.path)));
  if (JSON.stringify(actualPackages) !== JSON.stringify(expectedPackages)) fail('Installed package inventory differs from package-lock');
  return { config, plans: config.targets.map(spec => planFile(root, modules, spec, mode)) };
}
function atomicWrite(target, bytes) {
  const temp = `${target}.emergency-${randomUUID()}.tmp`;
  let descriptor;
  try {
    descriptor = fs.openSync(temp, 'wx', fs.statSync(target).mode);
    fs.writeFileSync(descriptor, bytes);
    fs.fsyncSync(descriptor);
    fs.closeSync(descriptor); descriptor = undefined;
    fs.renameSync(temp, target);
    if (hash(fs.readFileSync(target)) !== hash(bytes)) fail(`Write verification failed: ${target}`);
  } finally {
    if (descriptor !== undefined) fs.closeSync(descriptor);
    if (fs.existsSync(temp)) fs.unlinkSync(temp);
  }
}
function removeDeadOwner(lock) {
  ordinary(lock);
  const owner = JSON.parse(fs.readFileSync(lock, 'utf8'));
  if (!Number.isSafeInteger(owner.pid) || owner.pid < 1 || typeof owner.token !== 'string') fail('Invalid installer lock');
  let alive = true;
  try { process.kill(owner.pid, 0); } catch (probe) { if (probe.code === 'ESRCH') alive = false; }
  if (alive) fail('Another installer is active; retry after it finishes');
  if (fs.readFileSync(lock, 'utf8') !== JSON.stringify(owner)) fail('Installer lock changed');
  fs.unlinkSync(lock);
}
function acquire(lock) {
  const token = randomUUID();
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      fs.writeFileSync(lock, JSON.stringify({ pid: process.pid, token }), { flag: 'wx' });
      return token;
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
      removeDeadOwner(lock);
    }
  }
  fail('Could not acquire installer lock');
}
function applyJournal(journal, config, plans, mode) {
  const identity = { schema: 1, lock_sha256: config.lock_sha256, targets: plans.map(p => p.path) };
  if (fs.existsSync(journal)) {
    ordinary(journal);
    if (JSON.stringify(JSON.parse(fs.readFileSync(journal, 'utf8'))) !== JSON.stringify(identity)) fail('Unknown pending transaction');
    if (mode !== '--apply') fail('Incomplete transaction requires forward recovery');
  }
  const changes = plans.filter(p => !p.before.equals(p.after));
  if (changes.length) {
    if (!fs.existsSync(journal)) fs.writeFileSync(journal, JSON.stringify(identity), { flag: 'wx' });
    for (const plan of changes) atomicWrite(plan.target, plan.after);
  }
  if (mode !== '--check' && fs.existsSync(journal)) fs.unlinkSync(journal);
}
function release(lock, token) {
  if (!token || !fs.existsSync(lock)) return;
  ordinary(lock);
  const current = JSON.parse(fs.readFileSync(lock, 'utf8'));
  if (current.token === token && current.pid === process.pid) fs.unlinkSync(lock);
}
export function runMode(mode, root = app) {
  if (!['--apply', '--check', '--revert'].includes(mode)) fail('Use --apply or --check; revert is fixture-only');
  if (mode === '--revert') fixtureOnly(root);
  const lock = path.join(root, 'node_modules/.emergency-picomatch.lock');
  const journal = path.join(root, 'node_modules/.emergency-picomatch-journal.json');
  if (mode === '--check' && (fs.existsSync(lock) || fs.existsSync(journal))) fail('Pending mitigation transaction; apply before running tools');
  const token = mode === '--check' ? undefined : acquire(lock);
  try {
    const { config, plans } = loadPlan(root, mode);
    applyJournal(journal, config, plans, mode);
    return { mode, status: 'PASS', copies: plans.map(p => ({ path: p.path, version: p.version, sha256: hash(p.after), parsers: p.parsers })), warning: 'Temporary restrictions and work budget only. Trivy policy is unchanged; not an official fix. Restart existing tool processes after apply.' };
  } finally {
    release(lock, token);
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    if (process.argv.length > 3) fail('Unexpected arguments');
    console.log(JSON.stringify(runMode(process.argv[2] || '--check'), null, 2));
  } catch (error) { console.error(`PICOMATCH_MITIGATION_ERROR: ${error.message}`); process.exitCode = 1; }
}
