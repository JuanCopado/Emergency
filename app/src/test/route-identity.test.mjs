// @vitest-environment node
import { test, expect } from 'vitest';
import { identityProblems } from '../../scripts/route-identity.mjs';
import { registerTests } from './route-identity-cases.mjs';

// Explicit regression case for static test discovery (javascript:S2187).
// The SPA must not certify a 404 even when the expected page controls and heading are present.
test('pediatric route rejects HTTP 404 despite a matching heading and controls', () => {
  const observed = {
    pathname: '/pediatrics',
    httpStatus: 404,
    heading: 'Pediatría ambulatoria',
    mainVisible: true,
    probes: { 'main select': 2 },
    overlay: false,
    errors: [],
  };
  expect(identityProblems(observed, '/pediatrics')).toContain('HTTP_ERROR');
});

registerTests(test);
