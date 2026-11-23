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
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const PROTOTYPE_TOKENS = ['dermatologicFilter', 'r51-modality-entry', '.pdf,.txt,.csv,.json,.xml', 'DEC-CLIN-R14-01', 'Superficial visual description only'];
const defaultAppRoot = join(dirname(fileURLToPath(import.meta.url)), '..');

export function bundleText(directory) {
  return readdirSync(directory, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.js'))
    .map((entry) => readFileSync(join(entry.parentPath, entry.name), 'utf8'))
    .join('\n');
}

/** Builds one arm in development mode; only VITE_R51_PROTOTYPE differs. `exec` is injectable so the build can be tested. */
export function buildArm(prototypeFlag, { appRoot = defaultAppRoot, exec = execFileSync, baseEnv = process.env } = {}) {
  const viteBin = join(appRoot, 'node_modules', 'vite', 'bin', 'vite.js');
  const outDir = mkdtempSync(join(tmpdir(), 'emergency-hf-arm-'));
  try {
    const env = { ...baseEnv, NODE_ENV: 'development' };
    delete env.VITE_R51_PROTOTYPE;
    if (prototypeFlag) env.VITE_R51_PROTOTYPE = '1';
    exec(process.execPath, [viteBin, 'build', '--mode', 'development', '--outDir', outDir, '--emptyOutDir'], { cwd: appRoot, env, stdio: 'ignore' });
    return bundleText(outDir);
  } finally {
    rmSync(outDir, { recursive: true, force: true });
  }
}

export function sourceFiles(directory) {
  return readdirSync(directory, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && /\.(ts|tsx)$/.test(entry.name) && !/\.test\./.test(entry.name))
    .map((entry) => join(entry.parentPath, entry.name));
}

export function serverHash(root) {
  const files = readdirSync(root, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.py'))
    .map((entry) => join(entry.parentPath, entry.name))
    .sort();
  const hash = createHash('sha256');
  for (const file of files) hash.update(relative(root, file)).update('\0').update(readFileSync(file));
  return { files: files.length, sha256: hash.digest('hex') };
}

/** Pure evaluation of the two arms and of the wiring; returns the report (failures empty = preflight passed). */
export function evaluatePreflight({ armA, armB, sources, server }) {
  const failures = [];
  const report = { arm_a: { prototype_tokens_present: [] }, arm_b: { prototype_tokens_present: [] } };
  for (const token of PROTOTYPE_TOKENS) {
    if (armA.includes(token)) { report.arm_a.prototype_tokens_present.push(token); failures.push(`arm A (current interface) contains prototype token "${token}"`); }
    if (armB.includes(token)) report.arm_b.prototype_tokens_present.push(token);
    else failures.push(`arm B (prototype) lacks token "${token}"`);
  }
  const flagReaders = sources.filter((s) => s.text.includes('VITE_R51_PROTOTYPE')).map((s) => s.file);
  const mounts = sources.filter((s) => /from '\.\.?\/(clinical-note\/)?ModalityEntry'|from '\.\/ModalityEntry'/.test(s.text)).map((s) => s.file);
  report.flag_read_in = flagReaders;
  report.prototype_mounted_from = mounts;
  if (flagReaders.length !== 1 || !flagReaders[0].endsWith('r51Prototype.ts')) failures.push(`the flag must be read in r51Prototype.ts only (found: ${flagReaders.join(', ') || 'none'})`);
  if (mounts.length !== 1 || !mounts[0].endsWith('ClinicalNote.tsx')) failures.push(`the prototype must be mounted from ClinicalNote.tsx only (found: ${mounts.join(', ') || 'none'})`);
  report.server = server;   // one checkout, one server: identical for both arms by construction
  report.confounders_checked = ['same checkout', 'same build mode (development) for both arms', 'same server code hash for both arms', 'flag read and prototype mounted in one place each'];
  report.study_status = 'NOT_EXECUTED_PREFLIGHT_ONLY';
  report.failures = failures;
  return report;
}

export function runPreflight({ appRoot = defaultAppRoot, build = buildArm, exec = execFileSync } = {}) {
  const repoRoot = join(appRoot, '..');
  const sources = sourceFiles(join(appRoot, 'src')).map((file) => ({ file: relative(appRoot, file), text: readFileSync(file, 'utf8') }));
  return evaluatePreflight({
    armA: build(false, { appRoot, exec }),
    armB: build(true, { appRoot, exec }),
    sources,
    server: serverHash(join(repoRoot, 'clinical', 'scripts')),
  });
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const report = runPreflight();
  process.stdout.write(`${JSON.stringify(report, null, 1)}\n`);
  if (report.failures.length > 0) process.exit(1);
}
