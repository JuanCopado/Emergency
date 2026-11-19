import { expect, it } from 'vitest';
import { parseFiniteDecimal } from '../lib/format';

it.each(['1e-4000', '-1e-4000', '0.' + '0'.repeat(400) + '1'])('rejects nonzero input lost to underflow: %s', raw => {
  expect(parseFiniteDecimal(raw)).toBeNull();
});
it.each(['0', '0.000', '0e-4000', '-0.0'])('preserves explicit zero: %s', raw => {
  expect(parseFiniteDecimal(raw)).not.toBeNull();
  expect(parseFiniteDecimal(raw) === 0).toBe(true);
});
