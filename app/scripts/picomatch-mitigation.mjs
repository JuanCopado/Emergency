import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modules = path.join(app, 'node_modules');
const config = JSON.parse(fs.readFileSync(path.join(app, '../security/picomatch-mitigation.json'), 'utf8'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const fail = message => { throw new Error(message); };
const inside = target => {
  const relative = path.relative(modules, fs.realpathSync(target));
  if (relative.startsWith('..') || path.isAbsolute(relative)) fail(`Path outside local node_modules: ${target}`);
};
const plain = (target, directory = true) => {
  const stat = fs.lstatSync(target);
  if (stat.isSymbolicLink() || (directory ? !stat.isDirectory() : !stat.isFile())) fail(`Expected ordinary ${directory ? 'directory' : 'file'}: ${target}`);
  inside(target);
};

function inventory() {
  const found = [];
  function visitModules(directory) {
    plain(directory);
    for (const entry of fs.readdirSync(directory).sort((left, right) => left.localeCompare(right, 'en'))) {
      if (entry.startsWith('.')) continue;
      const target = path.join(directory, entry);
      plain(target);
      if (entry.startsWith('@')) {
        for (const child of fs.readdirSync(target).sort((left, right) => left.localeCompare(right, 'en'))) visitPackage(path.join(target, child));
      } else visitPackage(target);
    }
  }
  function visitPackage(directory) {
    plain(directory);
    if (path.basename(directory) === 'picomatch') found.push(directory);
    const nested = path.join(directory, 'node_modules');
    if (fs.existsSync(nested)) visitModules(nested);
  }
  visitModules(modules);
  const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json'), 'utf8'));
  const expected = Object.keys(lock.packages).filter(p => p.endsWith('/picomatch')).sort((left, right) => left.localeCompare(right, 'en'));
  const actual = found.map(p => path.relative(app, p).split(path.sep).join('/')).sort((left, right) => left.localeCompare(right, 'en'));
  if (JSON.stringify(expected) !== JSON.stringify(actual) || actual.length === 0) fail('Installed picomatch inventory differs from package-lock; use npm ci, then apply the guard.');
  return found;
}

function replaceAtomic(target, bytes) {
  const temporary = `${target}.${randomUUID()}.tmp`;
  let descriptor;
  let created = false;
  try {
    const mode = fs.statSync(target).mode;
    descriptor = fs.openSync(temporary, 'wx', mode);
    created = true;
    fs.fchmodSync(descriptor, mode);
    fs.writeFileSync(descriptor, bytes);
    fs.fsyncSync(descriptor);
    fs.closeSync(descriptor);
    descriptor = undefined;
    if (hash(fs.readFileSync(temporary)) !== hash(bytes)) fail(`Temporary write verification failed: ${target}`);
    fs.renameSync(temporary, target);
  } finally {
    try {
      if (descriptor !== undefined) fs.closeSync(descriptor);
    } finally {
      if (created && fs.existsSync(temporary)) fs.unlinkSync(temporary);
    }
  }
}

function rollback(written) {
  const errors = [];
  for (const plan of written.reverse()) {
    try {
      replaceAtomic(plan.target, plan.before);
      if (hash(fs.readFileSync(plan.target)) !== hash(plan.before)) fail('Rollback verification failed');
    } catch (error) {
      errors.push(`${plan.target}: ${error.message}`);
    }
  }
  return errors;
}

function main() {
  const mode = process.argv[2] || '--check';
  if (!['--apply', '--check', '--revert'].includes(mode) || process.argv.length > 3) fail('Use --apply, --check or --revert.');
  // Validate every installed copy before changing any file. Unknown versions/bytes fail closed.
  const plans = inventory().map(directory => {
    const packagePath = path.join(directory, 'package.json');
    const libPath = path.join(directory, 'lib');
    const target = path.join(libPath, 'parse.js');
    plain(packagePath, false); plain(libPath); plain(target, false);
    const version = JSON.parse(fs.readFileSync(packagePath, 'utf8')).version;
    const spec = config.versions[version];
    if (!spec) fail(`Unreviewed picomatch version ${version}; refusing to modify dependencies.`);
    const before = fs.readFileSync(target);
    const digest = hash(before);
    if (![spec.original_sha256, spec.patched_sha256].includes(digest)) fail(`Unknown parser bytes: ${target}`);
    const patched = digest === spec.patched_sha256;
    if (mode === '--check' && !patched) fail(`Guard absent: ${target}. Run npm run security:picomatch:apply.`);
    let after = before;
    if (mode === '--apply' && !patched) {
      const text = before.toString('utf8');
      if (text.split(config.anchor).length !== 2) fail('Parser anchor is ambiguous.');
      after = Buffer.from(text.replace(config.anchor, config.anchor + config.guard_block));
    }
    if (mode === '--revert' && patched) after = Buffer.from(before.toString('utf8').replace(config.guard_block, ''));
    const expected = mode === '--revert' ? spec.original_sha256 : spec.patched_sha256;
    if (hash(after) !== expected) fail(`Unexpected planned parser digest: ${target}`);
    return { target, version, before, after };
  });
  const written = [];
  try {
    for (const plan of plans) {
      if (!plan.before.equals(plan.after)) {
        replaceAtomic(plan.target, plan.after);
        written.push(plan);
        if (hash(fs.readFileSync(plan.target)) !== hash(plan.after)) fail(`Write verification failed: ${plan.target}`);
      }
    }
  } catch (error) {
    const rollbackErrors = rollback(written);
    if (rollbackErrors.length) fail(`${error.message}; rollback incomplete: ${rollbackErrors.join('; ')}`);
    throw error;
  }
  console.log(JSON.stringify({ mode, status: 'PASS', copies: plans.map(p => ({ path: path.relative(app, p.target).split(path.sep).join('/'), version: p.version, sha256: hash(p.after) })), warning: 'Temporary syntax restriction only; not an upstream parser fix. Run Trivy with its current official database and unchanged blocking policy.' }, null, 2));
}
try { main(); } catch (error) { console.error(`PICOMATCH_MITIGATION_ERROR: ${error.message}`); process.exitCode = 1; }
