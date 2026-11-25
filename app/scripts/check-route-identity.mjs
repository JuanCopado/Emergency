import assert from 'node:assert/strict';
import { contractFor, identityProblems } from './route-identity.mjs';

// Called only by browser QA. Counts are visible elements in main, never shell controls.
export async function inspectRoute(page, path, httpStatus, errors = []) {
  const contract = contractFor(path);
  // A SPA URL can change before Suspense replaces the previous module's heading.
  // Wait for the intended heading or an explicit not-found state, then read again
  // after the module controls are ready; never certify an intermediate old shell.
  await page.locator('main h1').filter({ hasText: new RegExp(`${contract.heading}|no encontrad[oa]|not found`, 'i') }).first().waitFor();
  const heading = (await page.locator('main h1').first().innerText()).trim();
  if (new RegExp(contract.heading).test(heading) && !/no encontrad[oa]|not found/i.test(heading)) {
    for (const selector of Object.keys(contract.controls)) await page.locator(selector).first().waitFor();
  }
  const probes = {};
  for (const selector of Object.keys(contract.controls)) {
    probes[selector] = await page.locator(selector).evaluateAll(elements => elements.filter(el => !!el.getClientRects().length).length);
  }
  const observed = { pathname: new URL(page.url()).pathname, httpStatus, heading: (await page.locator('main h1').first().innerText()).trim(),
    mainVisible: await page.locator('main').isVisible(), probes,
    overlay: await page.locator('vite-error-overlay, nextjs-portal').count() > 0, errors: [...errors] };
  const failures = identityProblems(observed, path);
  return { route: path, expected_valid: true, ...observed, failures, status: failures.length ? 'FAIL' : 'PASS' };
}

export async function assertRouteIdentity(page, path, httpStatus, errors = []) {
  const record = await inspectRoute(page, path, httpStatus, errors);
  assert.deepEqual(record.failures, [], `Expected valid module at ${path}: ${JSON.stringify(record)}`);
  return record;
}
