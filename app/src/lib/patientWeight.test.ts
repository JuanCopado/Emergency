import { describe, expect, it } from 'vitest';
import { isPatientWeight, parsePatientWeight } from './patientWeight';
import { buildTitrationTable, computeBolus, convertDose, doseToRate, rateToDose } from './infusion';

describe('explicit patient weight domain', () => {
  it.each(['', '0', '-1', '5e-324', '0.99999999999999999999', '180.000000000000000001',
    '181', 'NaN', 'Infinity', '1e99999999999999999999', '1e-99999999999999999999', '1,5', '70kg'])('rejects literal %s before rounding', value => {
    expect(parsePatientWeight(value)).toBeNull();
  });
  it.each([['1', 1], ['1.00000000000000000000', 1], ['.1e1', 1], ['70.125', 70.125],
    ['180', 180], ['180.000000000000000000', 180], ['1.8e2', 180], ['000180', 180]])('preserves permitted literal %s', (value, expected) => {
    expect(parsePatientWeight(String(value))).toBe(expected);
  });
  it.each([undefined, null, true, false, 0, Number.MIN_VALUE, .999, 181, NaN, Infinity, -Infinity, '70'])('does not coerce invalid runtime weight %s', value => {
    expect(isPatientWeight(value)).toBe(false);
  });
});

describe('infusion operations validate only the weight they need', () => {
  const concentration = { value: 1, unit: 'mg/mL' as const };
  it.each([0, Number.MIN_VALUE, .999, 181, NaN, Infinity, true as unknown as number])('rejects invalid weight %s in every weighted operation', weightKg => {
    expect(() => doseToRate({dose: 1, doseUnit: 'mg/kg/h', concentration, weightKg})).toThrow(/Weight/);
    expect(() => rateToDose({mlPerHour: 1, doseUnit: 'mg/kg/h', concentration, weightKg})).toThrow(/Weight/);
    expect(() => convertDose(1, 'mg/kg/h', 'mg/h', weightKg)).toThrow(/Weight/);
    expect(() => computeBolus({dosePerKg: 1, unit: 'mg/kg', concentration, weightKg})).toThrow(/Weight/);
    expect(buildTitrationTable({from: 1, to: 2, step: 1, doseUnit: 'mg/kg/h', concentration, weightKg})).toBeNull();
  });
  it.each([1, 70, 180])('preserves forward/reverse arithmetic at %s kg', weightKg => {
    const forward = doseToRate({dose: 1, doseUnit: 'mg/kg/h', concentration, weightKg});
    expect(forward.status).toBe('ok');
    if (forward.status === 'ok') expect(forward.mlPerHour).toBe(weightKg);
    expect(convertDose(1, 'mg/kg/h', 'mg/h', weightKg)).toBe(weightKg);
    expect(rateToDose({mlPerHour: weightKg, doseUnit: 'mg/kg/h', concentration, weightKg})).toMatchObject({status:'ok',dose:1});
  });
  it('keeps missing required weight blocked and fixed doses independent of weight', () => {
    expect(doseToRate({dose: 1, doseUnit: 'mg/kg/h', concentration})).toMatchObject({status:'needs-weight'});
    expect(rateToDose({mlPerHour: 1, doseUnit: 'mg/kg/h', concentration})).toMatchObject({status:'needs-weight'});
    expect(doseToRate({dose: 1, doseUnit: 'mg/h', concentration})).toMatchObject({status:'ok',mlPerHour:1});
    expect(doseToRate({dose: 1, doseUnit: 'mg/h', concentration, weightKg: .5})).toMatchObject({status:'ok',mlPerHour:1});
    expect(convertDose(1, 'mcg/min', 'mg/h')).toBe(.06);
  });
});
