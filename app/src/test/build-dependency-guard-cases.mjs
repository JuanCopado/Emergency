import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, unlinkSync, rmdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { assertDevOnlyMatcher, assertNoMatcherInBundle, assertNoMatcherInSourceMap, auditServiceWorker, productionDependencyGuard } from '../../scripts/build-dependency-guard.mjs';

export function registerTests(test, { integration = false } = {}) {
  const chunk = (modules = { '/project/src/main.tsx': {} }, imports = [], dynamicImports = []) => ({
    type: 'chunk', modules, imports, dynamicImports,
  });
  test('accepts both affected versions only as development dependencies', () => {
    assert.equal(assertDevOnlyMatcher({ lockfileVersion: 3, packages: {
      '': {},
      'node_modules/picomatch': { version: '2.3.2', dev: true },
      'node_modules/vite/node_modules/picomatch': { version: '4.0.7', dev: true },
    } }), 2);
  });
  for (const entry of [{ version: '4.0.7' }, { version: '2.3.2', dev: false }]) {
    test(`rejects a production matcher dependency with dev=${entry.dev}`, () => {
      assert.throws(() => assertDevOnlyMatcher({ lockfileVersion: 3, packages: { 'node_modules/picomatch': entry } }), /development-only/);
    });
  }
  test('accepts complete removal of the dependency', () => {
    assert.equal(assertDevOnlyMatcher({ lockfileVersion: 3, packages: { '': {} } }), 0);
  });
  test('fails closed on an unsupported lockfile schema', () => {
    for (const lock of [{}, { lockfileVersion: 2, packages: {} }, { lockfileVersion: 3 }]) {
      assert.throws(() => assertDevOnlyMatcher(lock), /lockfile/);
    }
  });
  test('accepts emitted application modules and ignores non-code assets', () => {
    assert.equal(assertNoMatcherInBundle({ 'app.js': chunk(), 'style.css': { type: 'asset' } }), 1);
  });
  for (const id of [
    '/repo/node_modules/picomatch/index.js',
    'C:\\repo\\node_modules\\vite\\node_modules\\picomatch\\lib\\parse.js',
    '\0/repo/node_modules/picomatch/index.js?commonjs-proxy',
    'picomatch', 'picomatch/lib/parse.js',
  ]) {
    test(`rejects emitted matcher module ${JSON.stringify(id)}`, () => {
      assert.throws(() => assertNoMatcherInBundle({ 'app.js': chunk({ [id]: {} }) }), /picomatch/);
    });
  }
  for (const field of ['imports', 'dynamicImports']) {
    test(`rejects external matcher ${field}`, () => {
      const output = chunk();
      output[field] = ['picomatch'];
      assert.throws(() => assertNoMatcherInBundle({ 'app.js': output }), /picomatch/);
    });
  }
  test('fails closed if no application modules were inspected', () => {
    for (const bundle of [{}, { 'app.js': chunk({}) }]) {
      assert.throws(() => assertNoMatcherInBundle(bundle), /No application modules/);
    }
  });
  test('accepts a service-worker source map with known runtime modules', () => {
    assert.equal(assertNoMatcherInSourceMap({ version: 3, sources: ['../node_modules/workbox-core/index.js'], mappings: 'AAAA' }), 1);
  });
  test('rejects matcher sources in a service-worker map', () => {
    assert.throws(() => assertNoMatcherInSourceMap({ version: 3, sources: ['../node_modules/picomatch/index.js'], mappings: 'AAAA' }), /picomatch/);
  });
  test('checks sourceRoot instead of trusting a relative source name', () => {
    assert.throws(() => assertNoMatcherInSourceMap({ version: 3, sourceRoot: '../node_modules/picomatch', sources: ['index.js'], mappings: 'AAAA' }), /picomatch/);
    assert.throws(() => assertNoMatcherInSourceMap({ version: 3, sourceRoot: 42, sources: ['index.js'], mappings: 'AAAA' }), /source map/);
  });
  test('does not reject unrelated source names', () => {
    assert.equal(assertNoMatcherInBundle({ 'app.js': chunk({ '/src/picomatch-example.js': {} }) }), 1);
  });
  test('rejects empty or malformed source maps instead of reporting absence', () => {
    for (const map of [{}, { version: 3, sources: [], mappings: '' }, { version: 3, sources: [42], mappings: 'AAAA' }]) {
      assert.throws(() => assertNoMatcherInSourceMap(map), /source map/);
    }
  });
  test('the build plugin blocks a contaminated emitted bundle', () => {
    const plugin = productionDependencyGuard();
    assert.equal(plugin.apply, 'build');
    assert.throws(() => plugin.generateBundle.call({}, {}, { 'app.js': chunk({ 'picomatch': {} }) }), /picomatch/);
  });
  test('the build plugin checks the real lock and reports inspected module count', () => {
    const plugin = productionDependencyGuard();
    plugin.buildStart();
    const messages = [];
    plugin.generateBundle.call({ info: message => messages.push(message) }, {}, { 'app.js': chunk() });
    assert.match(messages[0], /1 emitted modules; picomatch absent/);
  });
  test('audits the worker and separate Workbox runtime maps and fails closed', () => {
    const directory = mkdtempSync(join(tmpdir(), 'emergency-matcher-'));
    const files = ['sw.js', 'workbox-test.js', 'sw.js.map', 'workbox-test.js.map'];
    try {
      for (const file of files) writeFileSync(join(directory, file), file.endsWith('.map')
        ? JSON.stringify({ version: 3, sources: ['../node_modules/workbox-core/index.js'], mappings: 'AAAA' }) : '// synthetic');
      const output = pathToFileURL(directory + '/');
      assert.deepEqual(auditServiceWorker(output), { status: 'PASS', scope: 'service-worker-source-maps', maps: 2, sources: 2, advisory_status: 'OPEN' });
      writeFileSync(join(directory, 'workbox-test.js.map'), JSON.stringify({ version: 3, sources: ['../node_modules/picomatch/index.js'], mappings: 'AAAA' }));
      assert.throws(() => auditServiceWorker(output), /picomatch/);
      unlinkSync(join(directory, 'sw.js.map'));
      assert.throws(() => auditServiceWorker(output), /ENOENT/);
      unlinkSync(join(directory, 'sw.js'));
      assert.throws(() => auditServiceWorker(output), /Service worker missing/);
    } finally {
      for (const file of files) { try { unlinkSync(join(directory, file)); } catch (error) { if (error.code !== 'ENOENT') throw error; } }
      rmdirSync(directory);
    }
  });
  if (integration) {
    for (const contaminated of [false, true]) {
      test(`real Vite build ${contaminated ? 'blocks a matcher import' : 'accepts a clean entry'}`, async () => {
        const { build } = await import('vite');
        const directory = mkdtempSync(join(tmpdir(), 'emergency-rollup-'));
        const entry = join(directory, 'entry.js');
        const matcher = createRequire(import.meta.url).resolve('picomatch');
        try {
          writeFileSync(entry, contaminated
            ? `import matcher from ${JSON.stringify(matcher)}; globalThis.matcherProbe = matcher('*')('synthetic');`
            : 'export const synthetic = true;');
          const result = build({ configFile: false, logLevel: 'silent', plugins: [productionDependencyGuard()],
            build: { write: false, minify: false, lib: { entry, formats: ['es'] } } });
          if (contaminated) await assert.rejects(result, /picomatch found in distributed application code/);
          else assert.ok(await result);
        } finally {
          unlinkSync(entry);
          rmdirSync(directory);
        }
      });
    }
  }
}
