import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { contractFor, identityProblems, registeredPaths, matchesRegisteredRoute, assertRouteCoverage } from '../../scripts/route-identity.mjs';

const legacy = JSON.parse(readFileSync(new URL('../../scripts/fixtures/r55-browser-accessibility-audit.json', import.meta.url)));
const app = readFileSync(new URL('../App.tsx', import.meta.url), 'utf8');
const valid = () => ({ pathname: '/pediatrics', httpStatus: 200, heading: 'Pediatría ambulatoria', mainVisible: true,
  probes: { 'main select': 2 }, overlay: false, errors: [] });


export function registerTests(test) {
  test('both R55 browser reports marked the 404 pediatric page PASS; the gate rejects them', () => {
    for (const browser of Object.values(legacy.browsers)) {
      const row = browser.routes['/pediatric-outpatient'];
      assert.equal(row.status, 'PASS');
      assert.equal(row.heading, 'Página no encontrada');
      const problems = identityProblems({ ...valid(), pathname: '/pediatric-outpatient', heading: row.heading, probes: {} }, '/pediatrics');
      assert.ok(problems.includes('NOT_FOUND_PAGE'));
      assert.ok(problems.includes('WRONG_PATH'));
    }
  });

  test('R55 generic interactive controls never prove that the clinical score module rendered', () => {
    for (const browser of Object.values(legacy.browsers)) {
      assert.equal(browser.routes['/clinical-scores'].status, 'PASS');
      assert.throws(() => contractFor('/clinical-scores'), /No valid route contract/);
      const observed = { ...valid(), pathname: '/scores', heading: 'Scores clínicos', probes: {}, interactiveElementsCount: 17 };
      assert.ok(identityProblems(observed, '/scores').some(p => p.startsWith('MISSING_MODULE_CONTROL')));
    }
  });

  test('HTTP 404 cannot pass even with the correct heading and controls', () => {
    assert.ok(identityProblems({ ...valid(), httpStatus: 404 }, '/pediatrics').includes('HTTP_ERROR'));
  });

  test('a valid module requires exact page identity and module-specific evidence', () => {
    assert.deepEqual(identityProblems(valid(), '/pediatrics'), []);
    for (const change of [{ heading: '' }, { heading: 'Fármacos' }, { probes: {} }, { probes: { 'main select': 1 } }, { mainVisible: false }, { overlay: true }, { errors: ['chunk failed'] }, { errors: undefined }, { httpStatus: null }, { httpStatus: 199 }]) {
      assert.ok(identityProblems({ ...valid(), ...change }, '/pediatrics').length > 0, JSON.stringify(change));
    }
  });

  test('not-found pages are rejected independently of locale and the recorded status', () => {
    for (const heading of ['Página no encontrada', 'Page not found', 'Página não encontrada', 'Módulo no encontrado', 'Guía no encontrada', 'Procedimiento no encontrado']) {
      assert.ok(identityProblems({ ...valid(), heading, status: 'PASS' }, '/pediatrics').includes('NOT_FOUND_PAGE'));
    }
  });

  test('the router wildcard never makes a dangling link valid', () => {
    const paths = registeredPaths(app);
    assert.equal(matchesRegisteredRoute('/pediatrics?regimen=synthetic#test', paths), true);
    for (const path of ['/pediatric-outpatient', '/clinical-scores', '/no-such-route']) assert.equal(matchesRegisteredRoute(path, paths), false);
    assert.equal(matchesRegisteredRoute('/guides/sepsis-shock', paths), true);
    assertRouteCoverage(paths);
    assert.throws(() => assertRouteCoverage([...paths, '/new-module']), /Missing functional contract/);
    assert.throws(() => assertRouteCoverage(paths.filter(p => p !== '/')), /Contract has no registered route/);
    assert.throws(() => registeredPaths('<Route path={dynamic} />'), /Dynamic router paths/);
    assert.equal(matchesRegisteredRoute('/bad', ['*', '/pediatrics']), false);
  });
}
