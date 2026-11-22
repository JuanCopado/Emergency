// R14 · the inactive R5-1 prototype never reaches a production bundle, even if VITE_R51_PROTOTYPE=1 is set.
// Builds twice with the flag ON: a production build (the prototype code must be absent) and a
// non-production control (the same code must be present, so the check can detect it). Only the
// translation keys of the prototype legitimately ship in both. Synthetic only; no clinical data.
//
// Usage: node scripts/check-r51-flag-production.mjs
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const viteBin = join(appRoot, 'node_modules', 'vite', 'bin', 'vite.js');
// Code-only tokens: they exist in r51Prototype.ts / ModalityEntry.tsx and nowhere else (not in the locale JSON).
const CODE_TOKENS = ['dermatologicFilter', 'max-h-64 max-w-full', '.pdf,.txt,.csv,.json,.xml', 'r51-modality-entry'];

function bundleText(directory) {
  return readdirSync(directory, { recursive: true, withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.js'))
    .map((entry) => readFileSync(join(entry.parentPath, entry.name), 'utf8'))
    .join('\n');
}

function build(extraArgs, extraEnv) {
  const outDir = mkdtempSync(join(tmpdir(), 'emergency-r51-'));
  try {
    execFileSync(process.execPath, [viteBin, 'build', ...extraArgs, '--outDir', outDir, '--emptyOutDir'], {
      cwd: appRoot,
      env: { ...process.env, ...extraEnv, VITE_R51_PROTOTYPE: '1' },
      stdio: 'ignore',
    });
    return bundleText(outDir);
  } finally {
    rmSync(outDir, { recursive: true, force: true });
  }
}

const production = build([], {});
const control = build(['--mode', 'development'], { NODE_ENV: 'development' });

for (const token of CODE_TOKENS) {
  assert.ok(control.includes(token), `control build lacks "${token}": the check could not detect the prototype`);
  assert.ok(!production.includes(token), `production build contains prototype code ("${token}") with VITE_R51_PROTOTYPE=1`);
}
console.log(`ok  R5-1 prototype code absent from the production bundle with VITE_R51_PROTOTYPE=1 (${CODE_TOKENS.length} tokens; control build contains them)`);
