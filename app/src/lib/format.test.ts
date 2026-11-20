import { describe, expect, it } from 'vitest';
import { formatNumber, formatRate, parseDecimal } from './format';
describe('P3 canonical decimal input and localized output', () => {
  it.each(['1,000','0,1','1 000','1\u00a0000','1.000,5','1,000.5','NaN','Infinity','1e309','70kg'])('rejects ambiguous or invalid input %s', raw => expect(parseDecimal(raw)).toBeNull());
  it.each([['0.1',0.1],['1.000',1],['1000.5',1000.5],[' 70.5 ',70.5]] as const)('preserves canonical input %s', (raw, expected) => expect(parseDecimal(raw)).toBe(expected));
  it.each([['es-ES','0,1','1000,5'],['pt-PT','0,1','1000,5'],['en-GB','0.1','1000.5'],['zh-CN','0.1','1000.5']])('%s localizes the decimal without adding grouping', (locale,decimal,large) => {
    expect(formatNumber(0.1,locale)).toBe(decimal);expect(formatNumber(1000.5,locale)).toBe(large);expect(formatRate(1000.5,locale)).toBe(large);expect(formatNumber(3500,locale)).toBe('3500');
  });
  it.each([NaN,Infinity,-Infinity])('does not display a nonfinite pump rate', value => expect(formatRate(value,'es-ES')).toBe('—'));
});

import { formatCanonicalNumber, parseFiniteDecimal } from './format';
import { numericInput } from '../pediatrics/catalog';
import { parseNumber as parseInsulinNumber } from '../insulin/protocol';
it.each(['es-ES','pt-PT','en-GB','zh-CN'])('retains exact canonical decimals in %s', locale => {
  const decimal=locale.startsWith('es')||locale.startsWith('pt')?',':'.';
  expect(formatCanonicalNumber(0.000000123456789,locale)).toBe(`1${decimal}23456789e-7`);
  expect(formatCanonicalNumber(21.875,locale)).toBe(`21${decimal}875`);
  expect(formatCanonicalNumber(1000.5,locale)).toBe(`1000${decimal}5`);
});
it.each(['0,1','1,000','1 000','0x10','0b10','NaN','Infinity'])('rejects noncanonical %s in pediatric, insulin and shared input', raw => {
  expect(parseFiniteDecimal(raw)).toBeNull();expect(()=>numericInput(raw,'Fixture')).toThrow();expect(()=>parseInsulinNumber(raw,'Fixture')).toThrow();
});

it('preserves the integer gate across trailing decimal zeros', () => {
  const zeros = '0'.repeat(2048);
  expect(parseFiniteDecimal(`120.${zeros}`, true)).toBe(120);
  expect(parseFiniteDecimal(`120.${zeros}1`, true)).toBeNull();
});
