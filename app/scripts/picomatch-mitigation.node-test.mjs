import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { test, after } from 'node:test';

const app = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(import.meta.url);
const config = JSON.parse(fs.readFileSync(path.join(app, '../security/picomatch-mitigation.json'), 'utf8'));
const lock = JSON.parse(fs.readFileSync(path.join(app, 'package-lock.json'), 'utf8'));
const copies = Object.keys(lock.packages).filter(p => p.endsWith('/picomatch')).map(p => path.join(app, p));
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const control = mode => spawnSync(process.execPath, [path.join(app, 'scripts/picomatch-mitigation.mjs'), mode], { encoding: 'utf8', timeout: 20000 });
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'emergency-picomatch-test-'));
const originals = new Map();
const report = { baseline: [], guardedCopies: copies.length, benignComparisons: 0, rejectedCompilations: 0 };
after(() => {
  fs.rmSync(temp, { recursive: true, force: true });
  console.log('PICOMATCH_TEST_EVIDENCE ' + JSON.stringify(report));
});

for (const directory of copies) {
  const version = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8')).version;
  const target = path.join(directory, 'lib/parse.js');
  assert.equal(digest(fs.readFileSync(target)), config.versions[version].patched_sha256);
  if (!originals.has(version)) {
    const clone = path.join(temp, version);
    fs.cpSync(directory, clone, { recursive: true });
    const clean = Buffer.from(fs.readFileSync(path.join(clone, 'lib/parse.js'), 'utf8').replace(config.guard_block, ''));
    assert.equal(digest(clean), config.versions[version].original_sha256);
    fs.writeFileSync(path.join(clone, 'lib/parse.js'), clean);
    originals.set(version, require(clone));
  }
}

test('original versions reproduce bounded ReDoS probes in killable child processes', () => {
  for (const version of originals.keys()) {
    for (const pattern of ['+(*a)', '+(*)z', '*(*)z']) {
      const start = performance.now();
      const child = spawnSync(process.execPath, ['--max-old-space-size=128', '-e', "const pm=require(process.argv[1]);const re=pm.makeRe(process.argv[2]);console.log('compiled');console.log(re.test('a'.repeat(36)+'!'));", path.join(temp, version), pattern], { encoding: 'utf8', timeout: 1500, killSignal: 'SIGKILL' });
      assert.equal(child.error?.code, 'ETIMEDOUT', `${version} ${pattern}: expected bounded timeout`);
      assert.match(child.stdout, /compiled/);
      report.baseline.push({ version, pattern, timeoutMs: 1500, observedMs: Math.round(performance.now() - start), result: 'COMPILED_THEN_TIMEOUT_CHILD_KILLED' });
    }
  }
});

test('every installed copy rejects repeated extglobs across public APIs and fast paths', () => {
  const patterns = ['+(*)', '+(*a)', '+(*)z', '*(*)z', '*(a|*)z', '+(a|b)', 'src/+(*)/x', '**/+(*)', './*(*)z', '@(x|+(a))', '!(+(a))', '?(x|*(a))'];
  for (const directory of copies) {
    const pm = require(directory);
    const parser = require(path.join(directory, 'lib/parse.js'));
    for (const pattern of patterns) {
      for (const options of [{}, { fastpaths: false }, { dot: true }, { windows: true }, { bash: true }]) {
        for (const invoke of [() => pm(pattern, options), () => pm.isMatch('aaaa!', pattern, options), () => pm.makeRe(pattern, options), () => pm.parse(pattern, options), () => parser(pattern, options), () => pm(['*.js', pattern], options)]) {
          assert.throws(invoke, error => error instanceof SyntaxError && error.code === 'ERR_PICOMATCH_REPEATED_EXTGLOB', `${directory}: ${pattern} ${JSON.stringify(options)}`);
          report.rejectedCompilations++;
        }
      }
    }
  }
});

test('ordinary patterns and non-repeated extglobs preserve both versions matching behavior', () => {
  const patterns = ['*', '**', '**/*', '*.js', '**/*.{js,ts}', 'src/**/test?.[jt]s', '**/node_modules/**', '!**/*.test.ts', '**/*.{html,js,css,svg,png,woff2}', '**/*.map', 'assets/*-[a-z0-9]*.js', 'a{1..3}.txt', '{src,public}/**', '[ab]*', '[!ab]*', '.config/*', '?(*.js)', '@(a|b).ts', '!(*.test).js', 'foo/?(bar).js', '\\+(a)', '[+](a)', '"+(a)"', '\\*(a)', '[*](a)'];
  const samples = ['a', 'b', 'aaaa!', 'a.js', 'b.ts', 'a.test.js', 'a1.txt', 'a2.txt', 'a4.txt', 'src/a.js', 'src/x/test1.ts', 'public/index.html', '.config/a', '.hidden', 'assets/main-a3.js', 'foo/.dot.js', 'foo/bar.js', 'foo/.js', 'node_modules/a/x.js', 'x.map', '+(a)', '*(a)', 'a/b/c.js', ''];
  for (const directory of copies) {
    const pm = require(directory);
    const version = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8')).version;
    const before = originals.get(version);
    for (const options of [{}, { dot: true }, { nocase: true }, { fastpaths: false }, { windows: true }, { noextglob: true }]) {
      for (const pattern of patterns) {
        const cleanMatcher = before(pattern, options);
        const guardedMatcher = pm(pattern, options);
        assert.equal(pm.makeRe(pattern, options).source, before.makeRe(pattern, options).source);
        for (const sample of samples) {
          assert.equal(guardedMatcher(sample), cleanMatcher(sample), `${version}: ${pattern} ${sample}`);
          report.benignComparisons++;
        }
      }
    }
    // Disabled extglob parsing does not create the vulnerable repeated expression.
    for (const pattern of ['+(*)', '*(*)z', '+(a|b)']) assert.equal(pm.makeRe(pattern, { noextglob: true }).source, before.makeRe(pattern, { noextglob: true }).source);
  }
});

test('apply is idempotent, revert restores exact upstream bytes, check blocks unguarded installs', () => {
  assert.equal(control('--check').status, 0);
  assert.equal(control('--apply').status, 0);
  try {
    assert.equal(control('--revert').status, 0);
    for (const directory of copies) {
      const version = JSON.parse(fs.readFileSync(path.join(directory, 'package.json'), 'utf8')).version;
      assert.equal(digest(fs.readFileSync(path.join(directory, 'lib/parse.js'))), config.versions[version].original_sha256);
    }
    const absent = control('--check');
    assert.equal(absent.status, 1);
    assert.match(absent.stderr, /Guard absent/);
  } finally { assert.equal(control('--apply').status, 0); }
  assert.equal(control('--check').status, 0);
});

test('unknown bytes or versions prevent all writes and are never overwritten', () => {
  const snapshot = copies.map(p => ({ file: path.join(p, 'lib/parse.js'), bytes: fs.readFileSync(path.join(p, 'lib/parse.js')) }));
  const parser = snapshot.at(-1).file;
  const metadata = path.join(copies.at(-1), 'package.json');
  const metadataBytes = fs.readFileSync(metadata);
  try {
    // Earlier copies would need writing: a later integrity error must leave them untouched.
    const firstClean = Buffer.from(snapshot[0].bytes.toString('utf8').replace(config.guard_block, ''));
    fs.writeFileSync(snapshot[0].file, firstClean);
    const changed = Buffer.concat([snapshot.at(-1).bytes, Buffer.from('\n// deliberate isolated integrity probe\n')]);
    fs.writeFileSync(parser, changed);
    const refused = control('--apply');
    assert.equal(refused.status, 1);
    assert.match(refused.stderr, /Unknown parser bytes/);
    assert.deepEqual(fs.readFileSync(parser), changed);
    assert.deepEqual(fs.readFileSync(snapshot[0].file), firstClean);
    for (const item of snapshot.slice(1, -1)) assert.deepEqual(fs.readFileSync(item.file), item.bytes);
    fs.writeFileSync(snapshot[0].file, snapshot[0].bytes);
    fs.writeFileSync(parser, snapshot.at(-1).bytes);
    const modified = JSON.parse(metadataBytes.toString()); modified.version = '999.0.0';
    fs.writeFileSync(metadata, JSON.stringify(modified));
    const unknown = control('--apply');
    assert.equal(unknown.status, 1);
    assert.match(unknown.stderr, /Unreviewed picomatch version/);
    for (const item of snapshot) assert.deepEqual(fs.readFileSync(item.file), item.bytes);
  } finally {
    fs.writeFileSync(snapshot[0].file, snapshot[0].bytes);
    fs.writeFileSync(parser, snapshot.at(-1).bytes);
    fs.writeFileSync(metadata, metadataBytes);
  }
  assert.equal(control('--check').status, 0);
});

test('links outside the isolated dependency tree fail closed without writing their target', () => {
  const outside = path.join(temp, 'external-package'); fs.mkdirSync(outside);
  const sentinel = path.join(outside, 'sentinel.txt'); fs.writeFileSync(sentinel, 'unchanged');
  const link = path.join(app, 'node_modules/emergency-mitigation-link-probe');
  try {
    fs.symlinkSync(outside, link, process.platform === 'win32' ? 'junction' : 'dir');
    const refused = control('--apply');
    assert.equal(refused.status, 1);
    assert.match(refused.stderr, /Expected ordinary directory/);
    assert.equal(fs.readFileSync(sentinel, 'utf8'), 'unchanged');
  } finally { if (fs.existsSync(link)) fs.unlinkSync(link); }
  assert.equal(control('--check').status, 0);
});
