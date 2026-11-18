import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';
import { convert } from 'ast-v8-to-istanbul';
import { mergeProcessCovs } from '@bcoe/v8-coverage';
import { parseAstAsync } from 'vite';
import coverageLibrary from 'istanbul-lib-coverage';
import reportLibrary from 'istanbul-lib-report';
import reports from 'istanbul-reports';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
assert.deepEqual(process.argv.slice(2), ['--run'], 'Only a fresh test-and-capture run is accepted');
const filenames = ['scripts/picomatch-mitigation.mjs', 'scripts/picomatch-runtime-policy.cjs'];
const measuredFiles = filenames.map(filename => path.join(app, filename));
const evidenceFiles = [...measuredFiles, path.join(app, 'scripts/picomatch-mitigation.node-test.mjs'), path.join(app, '../security/picomatch-mitigation.json')];
const digest = file => createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const before = evidenceFiles.map(file => ({ file: path.relative(app, file).replaceAll('\\', '/'), sha256: digest(file) }));
const nonce = randomUUID();
const directory = fs.mkdtempSync(path.join(os.tmpdir(), `emergency-picomatch-v8-${nonce}-`));
const started = new Date();
try {
  const child = spawnSync(process.execPath, ['--test', 'scripts/picomatch-mitigation.node-test.mjs'], { cwd: app, env: { ...process.env, NODE_V8_COVERAGE: directory }, encoding: 'utf8', timeout: 180000 });
  assert.ifError(child.error); assert.equal(child.status, 0, child.stdout + child.stderr);
  assert.deepEqual(evidenceFiles.map(file => ({ file: path.relative(app, file).replaceAll('\\', '/'), sha256: digest(file) })), before, 'Executed source changed during coverage collection');
  const equivalent = filename => process.platform === 'win32' ? filename.toLowerCase() : filename;
  const captureFiles = fs.readdirSync(directory).filter(name => name.endsWith('.json'));
  assert.ok(captureFiles.length, 'No fresh V8 capture');
  const captures = captureFiles.map(name => {
    const file = path.join(directory, name);
    assert.ok(fs.statSync(file).mtimeMs >= started.getTime() - 2000, 'Stale capture');
    const raw = JSON.parse(fs.readFileSync(file, 'utf8'));
    return { result: raw.result.filter(script => script.url.startsWith('file:') && measuredFiles.some(file => equivalent(fileURLToPath(script.url)) === equivalent(file))) };
  });
  const merged = mergeProcessCovs(captures);
  assert.equal(merged.result.length, measuredFiles.length, 'Every runtime policy source must be measured');
  const map = coverageLibrary.createCoverageMap({});
  for (const capture of merged.result) {
    const file = fileURLToPath(capture.url), code = fs.readFileSync(file, 'utf8');
    map.merge(await convert({ ast: parseAstAsync(code), code, wrapperLength: 0, coverage: capture }));
  }
  const output = path.join(app, 'coverage/picomatch-measured'); fs.mkdirSync(output, { recursive: true });
  const context = reportLibrary.createContext({ dir: output, coverageMap: map });
  reports.create('lcovonly', { projectRoot: path.join(app, '..') }).execute(context);
  const native = fs.readFileSync(path.join(output, 'lcov.info'), 'utf8').replaceAll('\\', '/');
  const targets = filenames.map(file => `app/${file}`);
  for (const target of targets) assert.ok(native.includes(`SF:${target}\n`), `Missing measured record ${target}`);
  const lcovPath = path.join(app, 'coverage/lcov.info');
  const previous = fs.readFileSync(lcovPath, 'utf8');
  const records = previous.split(/(?<=end_of_record\n)/);
  const kept = records.filter(record => !targets.includes(record.match(/^SF:(.+)$/m)?.[1]?.replaceAll('\\', '/')));
  assert.equal(records.filter(record => record.includes('SF:app/scripts/picomatch-mitigation.mjs\n')).length, 1, 'Existing controller coverage record required');
  fs.writeFileSync(lcovPath, kept.join('') + native);
  const stats = map.getCoverageSummary().toJSON();
  const provenance = { nonce, startedUTC: started.toISOString(), completedUTC: new Date().toISOString(), sourceHashes: before, captures: captureFiles.map(name => ({ name, sha256: digest(path.join(directory, name)) })), source: 'Fresh successful bounded fixture tests; unchanged source hashes before/after; unique private capture directory', stats, otherLcovRecordsUnchanged: true };
  fs.writeFileSync(path.join(output, 'measured-summary.json'), JSON.stringify(provenance, null, 2) + '\n');
  console.log(JSON.stringify(provenance, null, 2));
} finally {
  assert.equal(path.dirname(directory), os.tmpdir());
  assert.ok(path.basename(directory).startsWith(`emergency-picomatch-v8-${nonce}-`));
  fs.rmSync(directory, { recursive: true, force: true });
}
