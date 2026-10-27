/**
 * S0-R2 — field-specific quantity validation (Q01–Q06 from the independent I01-R/X03 audit) and the
 * proposed pediatric contract policy A/B (prepared, not active). Shapes from
 * clinical/scripts/pediatric_outpatient_calculator.py; values are synthetic.
 */
import { describe, expect, it } from 'vitest';
import {
  PEDIATRIC_CONTRACT_POLICY_CURRENT,
  PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB,
  classifyPediatric,
  type Outcome,
} from './clinicalOutcome';

const report = { snapshot: { clinical_status: 'CLINICALLY_PENDING' }, sections: [['Resultado', ['x']]] };
const safety = { prescription_status: 'REVIEW_REQUIRED', blocked: false, alerts: [] };
const base = { regimen_id: 'fixture', drug: 'Fixture', status: 'calculated', medication_safety: safety };
const ok = (result: Record<string, unknown>, extra: Record<string, unknown> = {}) => ({ blocked: false, result: { ...base, ...result }, safety, export_report: report, ...extra });
const kind = (o: Outcome<unknown>) => o.kind;
const detail = (o: Outcome<unknown>) => (o.kind === 'ERROR' ? o.detail : '');
const QTY = 'a quantity is negative or not a number';

describe('S0-R2 Q01–Q06 (ordinary regressions)', () => {
  it.each([
    ['Q01 matched_band.duration_days = [-1, 5]', { matched_band: { duration_days: [-1, 5] } }],
    ['Q02 matched_band.duration_days = ["5", "7"]', { matched_band: { duration_days: ['5', '7'] } }],
    ['Q03 total_rehydration_ml = -1', { total_rehydration_ml: -1 }],
    ['Q04 target_ml_per_hour = "7"', { target_ml_per_hour: '7' }],
    ['Q05 drops_per_dose = "2"', { drops_per_dose: '2' }],
    ['Q06 volume_per_administration_ml = -1', { volume_per_administration_ml: -1 }],
  ])('%s → ERROR', (_name, patch) => {
    const o = classifyPediatric(ok(patch));
    expect(kind(o)).toBe('ERROR');
    expect(detail(o)).toBe(QTY);
    expect('result' in o).toBe(false);
  });
});

describe('S0-R2 types, finiteness and sign of the six fields', () => {
  it.each([
    ['duration_days string', { duration_days: '5' }],
    ['duration_days negative', { duration_days: -1 }],
    ['duration_days boolean', { duration_days: true }],
    ['duration_days object', { duration_days: { min: 5 } }],
    ['duration_days range of 3', { matched_band: { duration_days: [5, 7, 9] } }],
    ['duration_days range of 1', { matched_band: { duration_days: [5] } }],
    ['duration_days range with null', { matched_band: { duration_days: [5, null] } }],
    ['duration_days in a schedule phase', { schedule: [{ duration_days: -2 }] }],
    ['total_rehydration_ml string', { total_rehydration_ml: '750' }],
    ['total_rehydration_ml array', { total_rehydration_ml: [750] }],
    ['target_ml_per_hour negative', { target_ml_per_hour: -187.5 }],
    ['target_ml_per_hour object', { target_ml_per_hour: { value: 7 } }],
    ['volume_per_administration_ml string', { volume_per_administration_ml: '0.25' }],
    ['drops_per_dose negative', { drops_per_dose: -1 }],
    ['drops_per_dose boolean', { drops_per_dose: false }],
    ['drops_per_dose array', { drops_per_dose: [2] }],
    ['drops object: exact_drops string', { drops_per_dose: { exact_drops: '2.5', rounded_whole_drops: 3 } }],
    ['drops object: negative rounded drops', { drops_per_dose: { exact_drops: 2.5, rounded_whole_drops: -3 } }],
    ['drops object: negative mg_per_drop', { drops_per_dose: { mg_per_drop: -1 } }],
    ['drops object: rounding error as string', { drops_per_dose: { exact_drops: 2.5, rounding_error_percent: '5' } }],
  ])('%s → ERROR', (_name, patch) => {
    expect(detail(classifyPediatric(ok(patch)))).toBe(QTY);
  });

  it('non-finite values are rejected (NaN, Infinity)', () => {
    for (const patch of [{ total_rehydration_ml: Number.NaN }, { target_ml_per_hour: Number.POSITIVE_INFINITY }, { matched_band: { duration_days: [5, Number.NaN] } }]) {
      expect(kind(classifyPediatric(ok(patch)))).toBe('ERROR');
    }
  });
});

describe('S0-R2 legitimate values are preserved (no conversion, no rounding)', () => {
  it.each([
    ['duration_days integer', { duration_days: 5 }],
    ['duration_days null (backend omits)', { duration_days: null }],
    ['duration_days zero', { duration_days: 0 }],
    ['matched_band range', { matched_band: { duration_days: [5, 10] } }],
    ['matched_band range with decimals', { matched_band: { duration_days: [2.5, 10] } }],
    ['volume_ml_per_kg_course model', { dosing_weight_kg: 15, total_rehydration_ml: 750, administration_hours: 4, target_ml_per_hour: 187.5 }],
    ['topical drops_per_dose integer', { instructions: 'x', drops_per_dose: 4, volume_per_administration_ml: 0.25 }],
    ['drops conversion object with signed rounding error', { drops_per_dose: { exact_drops: 12.6, rounded_whole_drops: 13, mg_per_drop: 2, drops_per_ml: 20, delivered_mg_at_rounded_drops: 26, rounding_error_percent: -3.2, factor_source: 'registry_verified_exact_product', exact_product_name: 'X', drop_factor_source_url: null, warning: 'w' } }],
    ['drops conversion with null factors', { drops_per_dose: { exact_drops: 10, rounded_whole_drops: 10, mg_per_drop: null, drops_per_ml: 20, delivered_mg_at_rounded_drops: null, rounding_error_percent: null } }],
    ['sachet model without dose_mg', { dose_unit: 'sachet', sachets_per_day: 2, matched_band: { duration_days: [5, 7] } }],
    ['device model without dose_mg', { device: { label: 'spacer' }, doses_per_day: 2 }],
  ])('%s → SUCCESS with the value untouched', (_name, patch) => {
    const raw = ok(patch);
    const o = classifyPediatric(raw);
    expect(kind(o)).toBe('SUCCESS');
    if (o.kind === 'SUCCESS') expect(o.result.result).toBe(raw.result);
  });

  it('no universal validation: unrelated signed numbers are not touched', () => {
    expect(kind(classifyPediatric(ok({ matched_band: { min_age_months: 6, temperature_offset: -1 } })))).toBe('SUCCESS');
  });

  it('prototype keys are not field rules', () => {
    expect(kind(classifyPediatric(ok({ constructor: 'x', toString: 'y' })))).toBe('SUCCESS');
  });
});

describe('S0-R2 STOP/BLOCKED precedence unchanged', () => {
  it('BLOCKED and STOP win over a malformed quantity and never expose the result', () => {
    const bad = { total_rehydration_ml: -1 };
    const blocked = classifyPediatric({ ...ok(bad), blocked: true, safety: { alerts: [{ severity: 'STOP', message: 'm' }] } });
    const stop = classifyPediatric({ ...ok(bad), safety: { ...safety, alerts: [{ severity: 'STOP', message: 'm' }] } });
    expect(kind(blocked)).toBe('BLOCKED');
    expect(kind(stop)).toBe('STOP');
    expect('result' in blocked || 'result' in stop).toBe(false);
  });
});

describe('S0-R2 phase 2 — contract policy A/B (prepared, NOT active)', () => {
  it('current default policy has A and B off', () => {
    expect(PEDIATRIC_CONTRACT_POLICY_CURRENT).toEqual({ requireIdentity: false, requireExportReport: false });
    expect(Object.isFrozen(PEDIATRIC_CONTRACT_POLICY_CURRENT)).toBe(true);
    expect(Object.isFrozen(PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB)).toBe(true);
  });

  it('default behaviour is unchanged: minimal result and absent export_report still SUCCESS', () => {
    expect(kind(classifyPediatric({ blocked: false, result: { dose_mg: 7 }, safety }))).toBe('SUCCESS');
  });

  const AB = PEDIATRIC_CONTRACT_POLICY_PROPOSED_AB;
  it.each([
    ['A regimen_id missing', { result: { drug: 'X', status: 'calculated', dose_mg: 7 } }, 'regimen id is missing'],
    ['A regimen_id empty', { result: { regimen_id: ' ', drug: 'X', status: 'calculated' } }, 'regimen id is missing'],
    ['A drug missing', { result: { regimen_id: 'r', status: 'calculated' } }, 'drug is missing'],
    ['A drug empty', { result: { regimen_id: 'r', drug: '', status: 'calculated' } }, 'drug is missing'],
    ['A status missing', { result: { regimen_id: 'r', drug: 'X' } }, 'result status is not "calculated"'],
    ['A status different', { result: { regimen_id: 'r', drug: 'X', status: 'Calculated' } }, 'result status is not "calculated"'],
  ])('policy A/B: %s → ERROR', (_name, patch, message) => {
    expect(detail(classifyPediatric({ blocked: false, safety, export_report: report, ...patch }, AB))).toBe(message);
  });

  it('policy A/B: B export_report missing → ERROR; malformed → ERROR', () => {
    expect(detail(classifyPediatric({ blocked: false, safety, result: base }, AB))).toBe('export report is missing');
    expect(detail(classifyPediatric({ blocked: false, safety, result: base, export_report: { sections: [] } }, AB))).toBe('export report is malformed');
  });

  it('policy A/B does not require dose_mg: topical, device, sachet and volume-per-kg results are SUCCESS', () => {
    for (const extra of [{ instructions: 't', drops_per_dose: 2 }, { device: { label: 'd' } }, { dose_unit: 'sachet', sachets_per_day: 2 },
      { total_rehydration_ml: 750, target_ml_per_hour: 187.5 }]) {
      expect(kind(classifyPediatric(ok(extra), AB))).toBe('SUCCESS');
    }
  });

  it('policy A/B keeps BLOCKED/STOP precedence', () => {
    expect(kind(classifyPediatric({ blocked: true, safety: { alerts: [] } }, AB))).toBe('BLOCKED');
    expect(kind(classifyPediatric({ blocked: false, safety: { ...safety, alerts: [{ severity: 'STOP', message: 'm' }] }, result: {} }, AB))).toBe('STOP');
  });
});
