/**
 * S0-R — hardening of clinical guards (R1 alerts, R2 results and reports). Fail closed:
 * an incomplete or malformed response never reaches SUCCESS. Precedence BLOCKED > STOP > ERROR > SUCCESS.
 * Shapes from acute_medication_api.py (calculate_request) and pediatric_outpatient_api.py
 * (calculate_request) + pediatric_result_exporter.py (build_report); synthetic values only.
 */
import { describe, expect, it } from 'vitest';
import { classifyAcute, classifyPediatric, type Outcome } from './clinicalOutcome';

const report = { snapshot: { clinical_status: 'CLINICALLY_PENDING' }, sections: [['Estado y límites', ['CLINICALLY_PENDING']]] };
const acuteResult = { dose: 7, dose_unit: 'mg', pump_ml_h: null, monitoring_and_warnings: 'Advertencia' };
const acuteOk = { blocked: false, alerts: [], result: acuteResult, report };
const stop = { severity: 'STOP', code: 'CLINICAL_REVIEW_REQUIRED', message: 'Revisión requerida' };

// Real pediatric success shape: result (with regimen_id/status/medication_safety), safety, export_report.
const safety = { prescription_status: 'REVIEW_REQUIRED', blocked: false, alerts: [{ severity: 'CAUTION', code: 'c', message: 'Precaución', action: 'Revisar' }] };
const pedResult = { regimen_id: 'fixture', drug: 'Fixture', status: 'calculated', dose_mg: 7, doses_per_day: 3, duration_days: 5,
  volume_per_dose: { exact_ml: 2.5, rounded_0_1_ml: 2.5, concentration_mg_per_ml: null }, medication_safety: safety };
const pedOk = { blocked: false, result: pedResult, safety, export_report: report };

const omit = (o: Record<string, unknown>, key: string) => Object.fromEntries(Object.entries(o).filter(([k]) => k !== key));
const kind = (o: Outcome<unknown>) => o.kind;
const detail = (o: Outcome<unknown>) => (o.kind === 'ERROR' ? o.detail : '');
const hasResult = (o: Outcome<unknown>) => 'result' in o;

describe('S0-R R1 — acute alerts', () => {
  it('alerts field absent → ERROR (never SUCCESS)', () => {
    const noAlerts = omit(acuteOk, 'alerts');
    const o = classifyAcute(noAlerts);
    expect(kind(o)).toBe('ERROR');
    expect(detail(o)).toBe('alerts are missing');
  });
  it('empty alerts array is distinct and allows SUCCESS with a valid result and report', () => {
    expect(kind(classifyAcute(acuteOk))).toBe('SUCCESS');
  });
  it.each([
    ['not an array', 'STOP'],
    ['object', { message: 'm' }],
    ['item without message', [{ code: 'x' }]],
    ['empty message', [{ message: '  ' }]],
    ['numeric severity', [{ severity: 2, message: 'm' }]],
    ['numeric code', [{ code: 7, message: 'm' }]],
    ['object action', [{ action: {}, message: 'm' }]],
    ['null item', [null]],
  ])('malformed alerts (%s) → ERROR', (_n, alerts) => {
    const o = classifyAcute({ ...acuteOk, alerts });
    expect(kind(o)).toBe('ERROR');
    expect(detail(o)).toBe('alerts are malformed');
  });
  it('BLOCKED wins over absent or malformed alerts and never exposes a result', () => {
    const noAlerts = omit(acuteOk, 'alerts');
    for (const raw of [{ ...noAlerts, blocked: true }, { ...acuteOk, blocked: true, alerts: 'x' }, { ...acuteOk, blocked: true, alerts: [stop] }]) {
      const o = classifyAcute(raw);
      expect(kind(o)).toBe('BLOCKED');
      expect(hasResult(o)).toBe(false);
    }
  });
  it('STOP with a result present → STOP without result', () => {
    const o = classifyAcute({ ...acuteOk, alerts: [stop] });
    expect(o).toEqual({ kind: 'STOP', alerts: [stop] });
  });
});

describe('S0-R R2 — acute result and report', () => {
  it.each([
    ['report absent', { blocked: false, alerts: [], result: acuteResult }],
    ['report null', { ...acuteOk, report: null }],
    ['report without snapshot', { ...acuteOk, report: { sections: [] } }],
    ['sections not an array', { ...acuteOk, report: { snapshot: {}, sections: {} } }],
    ['section with non-string heading', { ...acuteOk, report: { snapshot: {}, sections: [[1, ['x']]] } }],
    ['section lines not strings', { ...acuteOk, report: { snapshot: {}, sections: [['h', [{ x: 1 }]]] } }],
    ['section wrong arity', { ...acuteOk, report: { snapshot: {}, sections: [['h']] } }],
  ])('%s → ERROR', (_n, raw) => {
    const o = classifyAcute(raw);
    expect(kind(o)).toBe('ERROR');
    expect(hasResult(o)).toBe(false);
  });
  it.each([
    ['dose as string', { dose: '7' }],
    ['negative dose as string', { dose: '-7' }],
    ['pump rate as string', { pump_ml_h: '12.5' }],
    ['negative withdrawal', { withdrawal_ml: -0.1 }],
    ['empty result', null],
  ])('%s → ERROR', (_n, patch) => {
    const result = patch === null ? {} : { ...acuteResult, ...patch };
    expect(kind(classifyAcute({ ...acuteOk, result }))).toBe('ERROR');
  });
  it('a valid report with empty sections is accepted (backend may send no lines)', () => {
    expect(kind(classifyAcute({ ...acuteOk, report: { snapshot: {}, sections: [] } }))).toBe('SUCCESS');
  });
});

describe('S0-R R1 — pediatric alerts', () => {
  it('safety.alerts absent → ERROR', () => {
    const o = classifyPediatric({ ...pedOk, safety: { prescription_status: 'OK' } });
    expect(kind(o)).toBe('ERROR');
    expect(detail(o)).toBe('alerts are missing');
  });
  it('safety absent → ERROR; safety not an object → ERROR', () => {
    const noSafety = omit(pedOk, 'safety');
    expect(detail(classifyPediatric(noSafety))).toBe('safety section is missing');
    expect(detail(classifyPediatric({ ...pedOk, safety: 'ok' }))).toBe('safety section is malformed');
  });
  it('empty alerts array with a valid result → SUCCESS', () => {
    expect(kind(classifyPediatric({ ...pedOk, safety: { ...safety, alerts: [] } }))).toBe('SUCCESS');
  });
  it.each([
    ['object instead of array', {}],
    ['item without message', [{ severity: 'INFO' }]],
    ['numeric severity', [{ severity: 1, message: 'm' }]],
    ['array action', [{ severity: 'INFO', message: 'm', action: ['x'] }]],
  ])('malformed alerts (%s) → ERROR', (_n, alerts) => {
    expect(detail(classifyPediatric({ ...pedOk, safety: { ...safety, alerts } }))).toBe('alerts are malformed');
  });
  it('BLOCKED with safety absent or alerts malformed → BLOCKED, no result', () => {
    const noSafety = omit(pedOk, 'safety');
    for (const raw of [{ ...noSafety, blocked: true }, { ...pedOk, blocked: true, safety: { alerts: 'x' } }]) {
      const o = classifyPediatric(raw);
      expect(kind(o)).toBe('BLOCKED');
      expect(hasResult(o)).toBe(false);
    }
  });
  it('STOP with result and blocked:false → STOP without result', () => {
    const o = classifyPediatric({ ...pedOk, safety: { ...safety, alerts: [stop] } });
    expect(kind(o)).toBe('STOP');
    expect(hasResult(o)).toBe(false);
  });
  it('prescription_status missing on success → ERROR', () => {
    expect(detail(classifyPediatric({ ...pedOk, safety: { alerts: [] } }))).toBe('prescription status is missing');
  });
});

describe('S0-R R2 — pediatric result', () => {
  it('empty result object → ERROR', () => {
    expect(detail(classifyPediatric({ ...pedOk, result: {} }))).toBe('result is empty');
  });
  it.each([
    ['dose as string', { dose_mg: '7' }],
    ['negative dose as string', { dose_mg: '-7' }],
    ['dose per kg as string', { dose_mg_per_kg: '15' }],
    ['boolean quantity', { total_doses: true }],
    ['nested volume as string', { volume_per_dose: { exact_ml: '2.5', rounded_0_1_ml: 2.5 } }],
    ['nested negative concentration', { volume_per_dose: { exact_ml: 2.5, concentration_mg_per_ml: -24 } }],
    ['schedule phase string', { schedule: [{ total_phase_doses: '6', estimated_phase_ml: 10 }] }],
    ['negative doses per day', { doses_per_day: -3 }],
  ])('%s → ERROR', (_n, patch) => {
    const o = classifyPediatric({ ...pedOk, result: { ...pedResult, ...patch } });
    expect(kind(o)).toBe('ERROR');
    expect(detail(o)).toBe('a quantity is negative or not a number');
  });
  it('regimen_id or status of the wrong type/value → ERROR', () => {
    expect(kind(classifyPediatric({ ...pedOk, result: { ...pedResult, regimen_id: 7 } }))).toBe('ERROR');
    expect(kind(classifyPediatric({ ...pedOk, result: { ...pedResult, status: 'error' } }))).toBe('ERROR');
  });
  it('contract variants stay valid: null concentration, duration range in a band, topical result without dose', () => {
    expect(kind(classifyPediatric(pedOk))).toBe('SUCCESS');
    expect(kind(classifyPediatric({ ...pedOk, result: { ...pedResult, matched_band: { duration_days: [5, 7], dose_mg: null } } }))).toBe('SUCCESS');
    expect(kind(classifyPediatric({ ...pedOk, result: { regimen_id: 'topical', drug: 'X', status: 'calculated', instructions: 'Aplicar', medication_safety: safety } }))).toBe('SUCCESS');
  });
  it('fields not required by the contract are not imposed (minimal synthetic result)', () => {
    expect(kind(classifyPediatric({ ...pedOk, result: { dose_mg: 7 } }))).toBe('SUCCESS');
  });
});

describe('S0-R R2 — pediatric export report', () => {
  it('absent export_report → SUCCESS with exportReport null (no export/print actions)', () => {
    const noReport = omit(pedOk, 'export_report');
    const o = classifyPediatric(noReport);
    expect(kind(o)).toBe('SUCCESS');
    if (o.kind === 'SUCCESS') expect(o.result.exportReport).toBeNull();
  });
  it.each([
    ['null', null],
    ['string', 'report'],
    ['no snapshot', { sections: [] }],
    ['bad section', { snapshot: {}, sections: [['h', 'not a list']] }],
  ])('malformed export_report (%s) → ERROR before any render or action', (_n, export_report) => {
    const o = classifyPediatric({ ...pedOk, export_report });
    expect(detail(o)).toBe('export report is malformed');
    expect(hasResult(o)).toBe(false);
  });
  it('valid export_report is passed through untouched', () => {
    const o = classifyPediatric(pedOk);
    if (o.kind !== 'SUCCESS') throw new Error('expected SUCCESS');
    expect(o.result.exportReport).toBe(report);
    expect(o.result.prescriptionStatus).toBe('REVIEW_REQUIRED');
  });
});

describe('S0-R precedence', () => {
  it('BLOCKED > STOP > ERROR > SUCCESS with malformed parts', () => {
    expect(kind(classifyPediatric({ blocked: true, safety: { alerts: [stop] }, result: {}, export_report: 'x' }))).toBe('BLOCKED');
    expect(kind(classifyPediatric({ blocked: false, safety: { alerts: [stop] }, result: {}, export_report: 'x' }))).toBe('STOP');
    expect(kind(classifyPediatric({ blocked: false, safety: { ...safety, alerts: [] }, result: {}, export_report: report }))).toBe('ERROR');
    expect(kind(classifyAcute({ blocked: false, alerts: [stop], result: null }))).toBe('STOP');
    expect(kind(classifyAcute({ blocked: false, alerts: [], result: acuteResult }))).toBe('ERROR');
  });
});
