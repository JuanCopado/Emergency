import { readFileSync, readdirSync } from 'node:fs';

export const auditBuild = process.env.EMERGENCY_SECURITY_AUDIT === '1';

function isMatcher(id) {
  const path = id.replaceAll('\\', '/').replaceAll('\0', '');
  return /(?:^|\/)node_modules\/picomatch(?:\/|\?|$)/.test(path)
    || /^picomatch(?:\/|\?|$)/.test(path);
}

export function assertDevOnlyMatcher(lock) {
  if (lock?.lockfileVersion !== 3 || !lock.packages || typeof lock.packages !== 'object') {
    throw new Error('Unsupported package lockfile; containment not verified');
  }
  const entries = Object.entries(lock.packages).filter(([path, entry]) => isMatcher(path) || entry.name === 'picomatch');
  if (entries.some(([, entry]) => entry.dev !== true)) {
    throw new Error('picomatch must remain development-only; advisory remains OPEN');
  }
  return entries.length;
}

export function assertNoMatcherInBundle(bundle) {
  const chunks = Object.values(bundle).filter(output => output.type === 'chunk');
  const modules = chunks.flatMap(chunk => Object.keys(chunk.modules));
  const references = chunks.flatMap(chunk => [...chunk.imports, ...chunk.dynamicImports]);
  if ([...modules, ...references].some(isMatcher)) {
    throw new Error('picomatch found in distributed application code; build rejected');
  }
  if (!modules.length) throw new Error('No application modules inspected; containment not verified');
  return modules.length;
}

export function assertNoMatcherInSourceMap(map) {
  if (map.version !== 3 || !Array.isArray(map.sources) || !map.sources.length
    || map.sources.some(source => typeof source !== 'string')
    || typeof map.mappings !== 'string' || !map.mappings.length) {
    throw new Error('Missing or malformed service-worker source map; containment not verified');
  }
  if (map.sourceRoot !== undefined && typeof map.sourceRoot !== 'string') {
    throw new Error('Malformed service-worker source map root; containment not verified');
  }
  if (map.sources.some(source => isMatcher(source) || isMatcher(`${map.sourceRoot || ''}/${source}`))) {
    throw new Error('picomatch found in distributed service-worker code; build rejected');
  }
  return map.sources.length;
}

export function productionDependencyGuard() {
  return {
    name: 'production-dependency-containment',
    apply: 'build',
    buildStart() {
      assertDevOnlyMatcher(JSON.parse(readFileSync(new URL('../package-lock.json', import.meta.url), 'utf8')));
    },
    generateBundle(_options, bundle) {
      const count = assertNoMatcherInBundle(bundle);
      this.info(`Containment PASS: ${count} emitted modules; picomatch absent; advisory remains OPEN`);
    },
  };
}

export function auditServiceWorker(output = new URL('../dist/', import.meta.url)) {
  // Workbox builds its own worker, outside the application's Rollup graph.
  // Inspect its generated source maps rather than relying on minified names.
  const files = readdirSync(output).filter(name => name === 'sw.js' || /^workbox-[\w-]+\.js$/.test(name));
  if (!files.includes('sw.js')) throw new Error('Service worker missing; containment not verified');
  const sources = files.reduce((count, name) => count + assertNoMatcherInSourceMap(
    JSON.parse(readFileSync(new URL(`${name}.map`, output), 'utf8')),
  ), 0);
  return { status: 'PASS', scope: 'service-worker-source-maps', maps: files.length, sources, advisory_status: 'OPEN' };
}

if (process.argv.includes('--check-service-worker')) {
  console.log(JSON.stringify(auditServiceWorker()));
}
