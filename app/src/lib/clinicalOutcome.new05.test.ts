/**
 * PEDIATRIC-SAFETY-01 — NEW-05 (MVP-E2E-01 E-07): a malformed pediatric quantity must never reach the
 * screen as a dose. The valid response is a real backend response for a bank case (synthetic inputs);
 * every malformed variant is derived from it by changing a single field.
 */
import { describe, expect, it } from 'vitest';
import fixture from './__fixtures__/pediatric-response-paracetamol-nominal.json';
import { classifyPediatric } from './clinicalOutcome';

type Json = Record<string, unknown>;
const clone = (): Json => JSON.parse(JSON.stringify(fixture.response)) as Json;
const withResult = (patch: (result: Json) => void) => { const raw = clone(); patch(raw.result as Json); return raw; };

describe('valid backend response', () => {
  it('is SUCCESS with its own dose_mg (number)', () => {
    const outcome = classifyPediatric(clone());
    expect(outcome.kind).toBe('SUCCESS');
    if (outcome.kind === 'SUCCESS') expect(typeof outcome.result.result.dose_mg).toBe('number');
  });
});

describe('NEW-05 — malformed dose_mg is an invalid response (no dose shown)', () => {
  it.each([
    ['text', 'abc'],
    ['numeric string', '225'],
    ['empty string', ''],
    ['boolean', true],
    ['object', {}],
    ['object with a number', { value: 225 }],
    ['array', [225]],
    ['negative', -1],
    ['NaN', Number.NaN],
    ['Infinity', Number.POSITIVE_INFINITY],
  ])('dose_mg %s → ERROR', (_name, value) => {
    expect(classifyPediatric(withResult((r) => { r.dose_mg = value; })).kind).toBe('ERROR');
  });

  it.each([
    ['volume_per_dose.exact_ml as text', (r: Json) => { (r.volume_per_dose as Json).exact_ml = 'x'; }],
    ['volume_per_dose.exact_ml as object', (r: Json) => { (r.volume_per_dose as Json).exact_ml = {}; }],
    ['dose_mg_per_kg as array', (r: Json) => { r.dose_mg_per_kg = [15]; }],
    ['total_doses as string', (r: Json) => { r.total_doses = '4'; }],
    ['estimated_total_course_ml negative', (r: Json) => { r.estimated_total_course_ml = -37.5; }],
  ])('%s → ERROR', (_name, patch) => {
    expect(classifyPediatric(withResult(patch)).kind).toBe('ERROR');
  });

  it('null dose_mg is the backend form of "no mg dose" for some models (topical, device…): accepted, never a number', () => {
    const outcome = classifyPediatric(withResult((r) => { r.dose_mg = null; }));
    expect(outcome.kind).toBe('SUCCESS');
  });

  it('an absent dose_mg is accepted (dose_mg is not required by every dose model) and nothing is invented', () => {
    const outcome = classifyPediatric(withResult((r) => { delete r.dose_mg; }));
    expect(outcome.kind).toBe('SUCCESS');
    if (outcome.kind === 'SUCCESS') expect(Object.hasOwn(outcome.result.result, 'dose_mg')).toBe(false);
  });
});

describe('structurally incomplete or incompatible responses', () => {
  it.each([
    ['not an object', () => 'x'],
    ['blocked flag missing', () => { const r = clone(); delete r.blocked; return r; }],
    ['safety missing', () => { const r = clone(); delete r.safety; return r; }],
    ['safety.alerts missing', () => { const r = clone(); delete (r.safety as Json).alerts; return r; }],
    ['prescription_status missing', () => { const r = clone(); delete (r.safety as Json).prescription_status; return r; }],
    ['result missing', () => { const r = clone(); delete r.result; return r; }],
    ['result empty', () => { const r = clone(); r.result = {}; return r; }],
    ['result status not "calculated"', () => withResult((r) => { r.status = 'draft'; })],
    ['export_report malformed', () => { const r = clone(); r.export_report = { sections: 'x' }; return r; }],
  ])('%s → ERROR', (_name, make) => {
    expect(classifyPediatric(make()).kind).toBe('ERROR');
  });

  it('blocked:true never yields figures, even with a malformed result', () => {
    const raw = withResult((r) => { r.dose_mg = 'abc'; }); raw.blocked = true;
    expect(classifyPediatric(raw).kind).toBe('BLOCKED');
  });

  it('a STOP alert stops the calculation', () => {
    const raw = clone(); (raw.safety as Json).alerts = [{ severity: 'STOP', message: 'synthetic STOP', action: '' }];
    expect(classifyPediatric(raw).kind).toBe('STOP');
  });
});
