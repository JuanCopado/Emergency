import { describe, expect, it } from 'vitest';
import { CLINICAL_DECIMAL_SEPARATOR, formatClinicalNumber, parseClinicalNumber } from './clinicalInput';

const ok = (text: string, allowNegative = false) => parseClinicalNumber(text, { allowNegative });

describe('parseClinicalNumber', () => {
  it.each([
    ['70', 70], ['100', 100], ['0', 0], ['70,5', 70.5], ['0,05', 0.05], ['1,25', 1.25], [' 70,5 ', 70.5], ['007', 7],
  ])('accepts %j → %d', (text, value) => {
    expect(ok(text)).toEqual({ ok: true, value });
  });

  it.each(['70.5', '0.05', '1.25', '1.000', '1.000,5', '1,000.5', '1,2,3', ',5', '70,', '1e2', '1E-3', '0x10', '0b1', '+70',
    '1 2', '7 0,5', 'NaN', 'Infinity', '-Infinity', '70kg', '−5', '٧٠'])('rejects %j as format', (text) => {
    expect(ok(text, true)).toEqual({ ok: false, reason: 'format' });
  });

  it.each(['', '   ', '\t'])('rejects %j as empty', (text) => {
    expect(ok(text)).toEqual({ ok: false, reason: 'empty' });
  });

  it('rejects magnitudes that overflow to Infinity', () => {
    expect(ok('9'.repeat(400))).toEqual({ ok: false, reason: 'nonfinite' });
  });

  it('allows negatives only when requested', () => {
    expect(ok('-1')).toEqual({ ok: false, reason: 'format' });
    expect(ok('-1,5', true)).toEqual({ ok: true, value: -1.5 });
    expect(ok('-0', true)).toEqual({ ok: true, value: 0 });
    expect(Object.is((ok('-0', true) as { value: number }).value, -0)).toBe(false);
  });

  it('keeps the parsed value identical to the dot-written JavaScript number (no rounding)', () => {
    for (const [text, dot] of [['0,1', '0.1'], ['0,30000000000000004', '0.30000000000000004'], ['12,345678901', '12.345678901']] as const) {
      expect(ok(text)).toEqual({ ok: true, value: Number(dot) });
    }
  });
});

describe('formatClinicalNumber', () => {
  it('uses comma as the only decimal separator', () => {
    expect(CLINICAL_DECIMAL_SEPARATOR).toBe(',');
    expect(formatClinicalNumber(0.05)).toBe('0,05');
    expect(formatClinicalNumber(70.5)).toBe('70,5');
    expect(formatClinicalNumber(-1.5)).toBe('-1,5');
  });

  it('keeps integers as integers and never adds thousands separators', () => {
    expect(formatClinicalNumber(70)).toBe('70');
    expect(formatClinicalNumber(0)).toBe('0');
    expect(formatClinicalNumber(1000)).toBe('1000');
    expect(formatClinicalNumber(12345.678, { maxDecimals: 1 })).toBe('12345,7');
  });

  it('shows full precision by default and never exponent notation', () => {
    expect(formatClinicalNumber(0.30000000000000004)).toBe('0,30000000000000004');
    expect(formatClinicalNumber(1e-7)).toBe('0,0000001');
    expect(formatClinicalNumber(1e21)).toBe('1000000000000000000000');
    expect(formatClinicalNumber(-2.5e-8)).toBe('-0,000000025');
  });

  it('rounds visually only when configured and keeps the input value untouched', () => {
    const value = 5.25;
    expect(formatClinicalNumber(value, { maxDecimals: 1 })).toBe('5,3');
    expect(formatClinicalNumber(value, { maxDecimals: 3 })).toBe('5,25');
    expect(value).toBe(5.25);
  });

  it('pads trailing zeros when minDecimals is set', () => {
    expect(formatClinicalNumber(5, { minDecimals: 1, maxDecimals: 1 })).toBe('5,0');
    expect(formatClinicalNumber(5, { minDecimals: 2 })).toBe('5,00');
  });

  it('never turns a non-zero value into a visual zero', () => {
    expect(formatClinicalNumber(0.004, { maxDecimals: 2 })).toBe('0,004');
    expect(formatClinicalNumber(-0.004, { maxDecimals: 2 })).toBe('-0,004');
    expect(formatClinicalNumber(1e-25, { maxDecimals: 3 })).toBe('0,0000000000000000000000001');
    expect(formatClinicalNumber(-0)).toBe('0');
  });

  it('returns null for non-finite values and rejects invalid options', () => {
    expect(formatClinicalNumber(Number.NaN)).toBeNull();
    expect(formatClinicalNumber(Number.POSITIVE_INFINITY)).toBeNull();
    expect(() => formatClinicalNumber(1, { maxDecimals: 1.5 })).toThrow(RangeError);
    expect(() => formatClinicalNumber(1, { minDecimals: 3, maxDecimals: 1 })).toThrow(RangeError);
  });

  it('round-trips through the parser', () => {
    for (const value of [0.05, 70.5, 1.25, 0, 1000, 0.1]) {
      expect(parseClinicalNumber(formatClinicalNumber(value) as string, { allowNegative: false })).toEqual({ ok: true, value });
    }
  });
});
