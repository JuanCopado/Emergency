import { describe, expect, it } from 'vitest';
import { classifyAcute, classifyPediatric, createRequestGuard, errorOutcome, type Outcome } from './clinicalOutcome';

// Structural fixtures copied from app/src/test/acute-medications.test.tsx:8-9 (no new clinical values).
const acuteResult = { dose: 7, dose_unit: 'mg', clinical_status: 'CLINICALLY_PENDING', monitoring_and_warnings: 'Advertencia canónica íntegra',
  components: { bolus_mg: 7, infusion_duration_min: 120 }, correction_ceiling_mmol_l: 8 };
const acuteOk = { blocked: false, alerts: [], result: acuteResult, report: { snapshot: acuteResult, sections: [] } };
const stopAlert = { severity: 'STOP', code: 'review', message: 'Revisión requerida' };

// Pediatric shape from pediatric_outpatient_api.py; values reuse the acute fixture.
const pediatricOk = { blocked: false, result: { dose_mg: 7, frequency: 'Fixture' },
  safety: { prescription_status: 'Fixture', alerts: [{ severity: 'CAUTION', message: 'Precaución', action: 'Revisar' }] },
  export_report: { snapshot: {}, sections: [] } };

const hasResult = (outcome: Outcome<unknown>) => 'result' in outcome;

describe('classifyAcute', () => {
  it('returns SUCCESS with the untouched result and report', () => {
    const outcome = classifyAcute(acuteOk);
    expect(outcome.kind).toBe('SUCCESS');
    if (outcome.kind === 'SUCCESS') {
      expect(outcome.result.result).toBe(acuteResult);
      expect(outcome.result.report).toBe(acuteOk.report);
    }
  });

  it('BLOCKED wins even when a result is present and never exposes it', () => {
    const outcome = classifyAcute({ ...acuteOk, blocked: true, alerts: [stopAlert] });
    expect(outcome).toEqual({ kind: 'BLOCKED', alerts: [stopAlert] });
    expect(hasResult(outcome)).toBe(false);
  });

  it('BLOCKED wins over malformed alerts', () => {
    expect(classifyAcute({ blocked: true, alerts: 'x' })).toEqual({ kind: 'BLOCKED', alerts: [] });
  });

  it('any alert is STOP, even with blocked=false and without severity', () => {
    const outcome = classifyAcute({ ...acuteOk, alerts: [{ code: 'review', message: 'Revisión requerida' }] });
    expect(outcome).toEqual({ kind: 'STOP', alerts: [{ severity: 'STOP', code: 'review', message: 'Revisión requerida' }] });
    expect(hasResult(outcome)).toBe(false);
  });

  it.each([
    ['null', null],
    ['array', []],
    ['missing blocked flag', { alerts: [], result: acuteResult }],
    ['non-boolean blocked', { ...acuteOk, blocked: 'false' }],
    ['malformed alerts', { ...acuteOk, alerts: [{ code: 'x' }] }],
    ['missing result', { blocked: false, alerts: [] }],
    ['null result', { ...acuteOk, result: null }],
    ['null dose', { ...acuteOk, result: { ...acuteResult, dose: null } }],
    ['string dose', { ...acuteOk, result: { ...acuteResult, dose: '7' } }],
    ['missing unit', { ...acuteOk, result: { ...acuteResult, dose_unit: null } }],
    ['empty unit', { ...acuteOk, result: { ...acuteResult, dose_unit: ' ' } }],
    ['negative dose', { ...acuteOk, result: { ...acuteResult, dose: -7 } }],
    ['negative pump rate', { ...acuteOk, result: { ...acuteResult, pump_ml_h: -1 } }],
    ['NaN dose', { ...acuteOk, result: { ...acuteResult, dose: Number.NaN } }],
    ['Infinity in a nested value', { ...acuteOk, result: { ...acuteResult, components: { bolus_mg: Number.POSITIVE_INFINITY } } }],
  ])('%s → ERROR INVALID_RESPONSE', (_, raw) => {
    const outcome = classifyAcute(raw);
    expect(outcome.kind).toBe('ERROR');
    if (outcome.kind === 'ERROR') expect(outcome.reason).toBe('INVALID_RESPONSE');
  });

  it('zero dose and absent optional quantities remain SUCCESS', () => {
    expect(classifyAcute({ ...acuteOk, result: { ...acuteResult, dose: 0 } }).kind).toBe('SUCCESS');
    expect(classifyAcute({ ...acuteOk, result: { ...acuteResult, pump_ml_h: null } }).kind).toBe('SUCCESS');
  });
});

describe('classifyPediatric', () => {
  it('returns SUCCESS keeping non-STOP alerts, result, export report and status', () => {
    const outcome = classifyPediatric(pediatricOk);
    expect(outcome.kind).toBe('SUCCESS');
    if (outcome.kind === 'SUCCESS') {
      expect(outcome.result.result).toBe(pediatricOk.result);
      expect(outcome.result.exportReport).toBe(pediatricOk.export_report);
      expect(outcome.result.prescriptionStatus).toBe('Fixture');
      expect(outcome.alerts).toHaveLength(1);
    }
  });

  it('BLOCKED wins and never exposes the result', () => {
    const outcome = classifyPediatric({ ...pediatricOk, blocked: true, safety: { alerts: [stopAlert] } });
    expect(outcome.kind).toBe('BLOCKED');
    expect(hasResult(outcome)).toBe(false);
  });

  it.each([
    ['STOP with blocked=false', 'STOP'],
    ['unknown severity', 'SEVERE'],
    ['lower-case severity', 'caution'],
    ['empty severity', ''],
  ])('%s → STOP without result', (_, severity) => {
    const outcome = classifyPediatric({ ...pediatricOk, safety: { ...pediatricOk.safety, alerts: [{ severity, message: 'm' }] } });
    expect(outcome.kind).toBe('STOP');
    expect(hasResult(outcome)).toBe(false);
  });

  it('missing severity → STOP', () => {
    expect(classifyPediatric({ ...pediatricOk, safety: { ...pediatricOk.safety, alerts: [{ message: 'm' }] } }).kind).toBe('STOP');
  });

  it('STOP mixed with CAUTION → STOP', () => {
    const alerts = [{ severity: 'CAUTION', message: 'c' }, { severity: 'STOP', message: 's' }];
    expect(classifyPediatric({ ...pediatricOk, safety: { ...pediatricOk.safety, alerts } }).kind).toBe('STOP');
  });

  it.each([
    ['null', null],
    ['missing blocked flag', { result: pediatricOk.result, safety: pediatricOk.safety }],
    ['missing safety', { blocked: false, result: pediatricOk.result }],
    ['malformed alerts', { ...pediatricOk, safety: { alerts: {} } }],
    ['missing result', { blocked: false, safety: pediatricOk.safety }],
    ['negative nested volume', { ...pediatricOk, result: { volume_per_dose: { exact_ml: -1 } } }],
    ['NaN dose', { ...pediatricOk, result: { dose_mg: Number.NaN } }],
  ])('%s → ERROR INVALID_RESPONSE', (_, raw) => {
    expect(classifyPediatric(raw).kind).toBe('ERROR');
  });

  it('zero values remain SUCCESS', () => {
    expect(classifyPediatric({ ...pediatricOk, result: { dose_mg: 0 } }).kind).toBe('SUCCESS');
  });
});

describe('precedence and helpers', () => {
  it('BLOCKED > STOP > ERROR > SUCCESS', () => {
    const malformedResult = { result: null };
    expect(classifyAcute({ blocked: true, alerts: [stopAlert], ...malformedResult }).kind).toBe('BLOCKED');
    expect(classifyAcute({ blocked: false, alerts: [stopAlert], ...malformedResult }).kind).toBe('STOP');
    expect(classifyAcute({ blocked: false, alerts: [], ...malformedResult }).kind).toBe('ERROR');
  });

  it('errorOutcome builds network and HTTP errors', () => {
    expect(errorOutcome('NETWORK', 'offline')).toEqual({ kind: 'ERROR', reason: 'NETWORK', detail: 'offline' });
  });

  it('request guard accepts only the latest request', () => {
    const guard = createRequestGuard();
    const first = guard.next();
    const second = guard.next();
    expect(guard.isCurrent(first)).toBe(false);
    expect(guard.isCurrent(second)).toBe(true);
    guard.invalidate();
    expect(guard.isCurrent(second)).toBe(false);
  });
});
