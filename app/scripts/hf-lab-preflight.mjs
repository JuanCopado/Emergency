// R21 · preflight of the isolated A/B laboratory for the human-factors Stage 1 (no participants, no study).
// Arm A = the current interface; arm B = the inactive R5-1 prototype. Both arms are built from the SAME checkout in the
// SAME non-production mode (so minification and mode do not confound the comparison); only VITE_R51_PROTOTYPE differs.
// The script proves that (1) arm A carries no prototype code, (2) arm B carries it (and the approved texts),
// (3) the flag is read in one single place and the prototype is mounted from one single place, and
// (4) the server code is the same for both arms (SHA-256 reported). It never touches production builds or clinical data.
//
// Usage: node scripts/hf-lab-preflight.mjs   (prints one JSON report; exit code 1 on any failed check)
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = join(appRoot, '..');
const viteBin = join(appRoot, 'node_modules', 'vite', 'bin', 'vite.js');
// Code-only tokens (they exist in the prototype sources and nowhere else; not in the locale JSON).
const PROTOTYPE_TOKENS = ['dermatologicFilter', 'r51-modality-entry', '.pdf,.txt,.csv,.json,.xml', 'DEC-CLIN-R14-01', 'Superficial visual description only'];

function bundleText(directory) {
  return readdirSync(directory, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.js'))
    .map((entry) => readFileSync(join(entry.parentPath, entry.name), 'utf8'))
    .join('\n');
}

function buildArm(prototypeFlag) {
  const outDir = mkdtempSync(join(tmpdir(), 'emergency-hf-arm-'));
  try {
    const env = { ...process.env, NODE_ENV: 'development' };
    delete env.VITE_R51_PROTOTYPE;
    if (prototypeFlag) env.VITE_R51_PROTOTYPE = '1';
    execFileSync(process.execPath, [viteBin, 'build', '--mode', 'development', '--outDir', outDir, '--emptyOutDir'], { cwd: appRoot, env, stdio: 'ignore' });
    return bundleText(outDir);
  } finally {
    rmSync(outDir, { recursive: true, force: true });
  }
}

function sourceFiles(directory) {
  return readdirSync(directory, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && /\.(ts|tsx)$/.test(entry.name) && !/\.test\./.test(entry.name))
    .map((entry) => join(entry.parentPath, entry.name));
}

function serverHash() {
  const root = join(repoRoot, 'clinical', 'scripts');
  const files = readdirSync(root, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.py'))
    .map((entry) => join(entry.parentPath, entry.name))
    .sort();
  const hash = createHash('sha256');
  for (const file of files) hash.update(relative(root, file)).update('\0').update(readFileSync(file));
  return { files: files.length, sha256: hash.digest('hex') };
}

const armA = buildArm(false);
const armB = buildArm(true);
const failures = [];
const report = { arm_a: { prototype_tokens_present: [] }, arm_b: { prototype_tokens_present: [] } };
for (const token of PROTOTYPE_TOKENS) {
  if (armA.includes(token)) { report.arm_a.prototype_tokens_present.push(token); failures.push(`arm A (current interface) contains prototype token "${token}"`); }
  if (armB.includes(token)) report.arm_b.prototype_tokens_present.push(token);
  else failures.push(`arm B (prototype) lacks token "${token}"`);
}

const sources = sourceFiles(join(appRoot, 'src')).map((file) => ({ file: relative(appRoot, file), text: readFileSync(file, 'utf8') }));
const flagReaders = sources.filter((s) => s.text.includes('VITE_R51_PROTOTYPE')).map((s) => s.file);
const mounts = sources.filter((s) => /from '\.\.?\/(clinical-note\/)?ModalityEntry'|from '\.\/ModalityEntry'/.test(s.text)).map((s) => s.file);
report.flag_read_in = flagReaders;
report.prototype_mounted_from = mounts;
if (flagReaders.length !== 1 || !flagReaders[0].endsWith('r51Prototype.ts')) failures.push(`the flag must be read in r51Prototype.ts only (found: ${flagReaders.join(', ') || 'none'})`);
if (mounts.length !== 1 || !mounts[0].endsWith('ClinicalNote.tsx')) failures.push(`the prototype must be mounted from ClinicalNote.tsx only (found: ${mounts.join(', ') || 'none'})`);

report.server = serverHash();   // one checkout, one server: identical for both arms by construction
report.confounders_checked = ['same checkout', 'same build mode (development) for both arms', 'same server code hash for both arms', 'flag read and prototype mounted in one place each'];
report.study_status = 'NOT_EXECUTED_PREFLIGHT_ONLY';
report.failures = failures;
process.stdout.write(`${JSON.stringify(report, null, 1)}\n`);
if (failures.length > 0) process.exit(1);
