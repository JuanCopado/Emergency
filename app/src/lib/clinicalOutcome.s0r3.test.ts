/**
 * S0-R3 — residual pediatric quantity fields. Shapes verified in pediatric_outpatient_calculator.py,
 * the pediatric catalog and the real response bank; values are synthetic.
 */
import { describe, expect, it } from 'vitest';
import { PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB, classifyPediatric, type Outcome } from './clinicalOutcome';

const report = { snapshot: { clinical_status: 'CLINICALLY_PENDING' }, sections: [['Resultado', ['x']]] };
const safety = { prescription_status: 'REVIEW_REQUIRED', blocked: false, alerts: [] };
const base = { regimen_id: 'fixture', drug: 'Fixture', status: 'calculated', medication_safety: safety };
const ok = (result: Record<string, unknown>) => ({ blocked: false, result: { ...base, ...result }, safety, export_report: report });
const kind = (o: Outcome<unknown>) => o.kind;
const QTY = 'a quantity is negative or not a number';

describe('S0-R3 residual defects → ERROR without result', () => {
  it.each([
    ['administration_hours negative', { administration_hours: -1 }],
    ['dose_ml as string', { matched_band: { dose_ml: '5' } }],
    ['dose_ml_range with strings', { matched_band: { dose_ml_range: ['5', '10'] } }],
    ['dose_ml_range with a negative', { matched_band: { dose_ml_range: [-5, 10] } }],
    ['dose_ml_range of 3', { matched_band: { dose_ml_range: [5, 10, 20] } }],
    ['dose_ml_range as object', { matched_band: { dose_ml_range: { min: 5, max: 10 } } }],
    ['doses_per_day_range with a boolean', { doses_per_day_range: [true, 6] }],
    ['doses_per_day_range with null inside', { doses_per_day_range: [4, null] }],
    ['doses_per_day_range as string', { doses_per_day_range: '4-6' }],
    ['applications_per_day negative', { applications_per_day: -2 }],
    ['repeat_after_days negative', { repeat_after_days: -7 }],
    ['drops_per_dose as empty object', { drops_per_dose: {} }],
    ['drops_per_dose object without rounded_whole_drops', { drops_per_dose: { exact_drops: 12.6 } }],
    ['drops_per_dose object with fractional rounded drops', { drops_per_dose: { exact_drops: 12.6, rounded_whole_drops: 12.6 } }],
    ['drops_per_dose empty object in a schedule phase', { schedule: [{ dose_mg: 5, drops_per_dose: {} }] }],
    ['administration_hours as string', { administration_hours: '4' }],
    ['dose_ml NaN', { matched_band: { dose_ml: Number.NaN } }],
  ])('%s', (_name, patch) => {
    const o = classifyPediatric(ok(patch));
    expect(kind(o)).toBe('ERROR');
    if (o.kind === 'ERROR') expect([QTY, 'result contains a non-finite number']).toContain(o.detail);
    expect('result' in o).toBe(false);
  });
});

describe('S0-R3 real shapes stay SUCCESS and untouched', () => {
  it.each([
    ['volume_ml_per_kg_course', { dosing_weight_kg: 15, total_rehydration_ml: 750, administration_hours: 4.0, target_ml_per_hour: 187.5 }],
    ['fixed_volume_band with dose_ml', { matched_band: { dose_ml: 2.5, dose_ml_range: null }, volume_per_dose: { exact_ml: 2.5, rounded_0_1_ml: 2.5, concentration_mg_per_ml: null }, dose_unit: 'mL' }],
    ['fixed_volume_band with dose_ml_range', { matched_band: { dose_ml: null, dose_ml_range: [2.5, 10] }, dose_unit: 'mL' }],
    ['topical with ranges and pass-through counts', { instructions: 't', drops_per_dose: 4, doses_per_day_range: [4, 6], applications_per_day: 2, repeat_after_days: 7 }],
    ['topical with nulls', { instructions: 't', applications_per_day: null, repeat_after_days: null, doses_per_day_range: null }],
    ['_drops() conversion object', { drops_per_dose: { exact_drops: 12.6, rounded_whole_drops: 13, mg_per_drop: 2, drops_per_ml: 20, delivered_mg_at_rounded_drops: 26, rounding_error_percent: -3.2, factor_source: 'registry_verified_exact_product', exact_product_name: 'X', drop_factor_source_url: null, warning: 'w' } }],
  ])('%s', (_name, patch) => {
    const raw = ok(patch);
    const o = classifyPediatric(raw);
    expect(kind(o)).toBe('SUCCESS');
    if (o.kind === 'SUCCESS') expect(o.result.result).toBe(raw.result);
    expect(kind(classifyPediatric(raw, PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB))).toBe('SUCCESS');
  });

  it('BLOCKED and STOP still win over a malformed residual field', () => {
    const bad = { drops_per_dose: {} };
    expect(kind(classifyPediatric({ ...ok(bad), blocked: true }))).toBe('BLOCKED');
    expect(kind(classifyPediatric({ ...ok(bad), safety: { ...safety, alerts: [{ severity: 'STOP', message: 'm' }] } }))).toBe('STOP');
  });
});
