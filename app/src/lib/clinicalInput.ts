/**
 * S0 — clinical numeric input and decimal display policy.
 *
 * Policy: in the clinical interface every decimal is written and shown with a comma.
 * A decimal point is rejected on input and never produced on output. Parsing only
 * converts text to a JavaScript number; it never rounds, truncates, applies clinical
 * limits or changes the value sent to the backend.
 */

export const CLINICAL_DECIMAL_SEPARATOR = ',';

export type ParseFailure = 'empty' | 'format' | 'nonfinite';
export type ParseResult = { ok: true; value: number } | { ok: false; reason: ParseFailure };

// Optional '-', ASCII digits, optional ',' followed by at least one digit. Nothing else:
// no '.', no exponent, no '+', no hexadecimal, no thousands separators, no inner spaces.
const CLINICAL_NUMBER = /^(-?)(\d+)(?:,(\d+))?$/;

export function parseClinicalNumber(text: string, opts: { allowNegative: boolean }): ParseResult {
  const trimmed = text.trim();
  if (!trimmed) return { ok: false, reason: 'empty' };
  const match = CLINICAL_NUMBER.exec(trimmed);
  if (!match) return { ok: false, reason: 'format' };
  const [, sign, integer, fraction] = match;
  if (sign && !opts.allowNegative) return { ok: false, reason: 'format' };
  const value = Number(`${sign}${integer}${fraction === undefined ? '' : `.${fraction}`}`);
  if (!Number.isFinite(value)) return { ok: false, reason: 'nonfinite' };
  // -0 carries no clinical meaning and would display as "-0".
  return { ok: true, value: Object.is(value, -0) ? 0 : value };
}

export type ClinicalFormatOptions = {
  /** Visual rounding only; omit to show the value with full precision. Integer 0–20. */
  maxDecimals?: number;
  /** Trailing zeros to keep (e.g. 1 for a pump rate shown as "5,0"). Integer 0–20, ≤ maxDecimals. */
  minDecimals?: number;
};

const MAX_DECIMALS = 20;

function digits(n: number | undefined, fallback: number): number {
  if (n === undefined) return fallback;
  if (!Number.isInteger(n) || n < 0 || n > MAX_DECIMALS) throw new RangeError('decimals must be an integer between 0 and 20');
  return n;
}

/** Shortest round-trip decimal of a finite number, without exponent notation. */
function plainDecimal(value: number): string {
  const text = String(value);
  const exp = /^(-?)(\d)(?:\.(\d+))?e([+-]\d+)$/.exec(text);
  if (!exp) return text;
  const [, sign, lead, rest = '', power] = exp;
  const mantissa = lead + rest;
  const point = 1 + Number(power);
  if (point <= 0) return `${sign}0.${'0'.repeat(-point)}${mantissa}`;
  if (point >= mantissa.length) return `${sign}${mantissa}${'0'.repeat(point - mantissa.length)}`;
  return `${sign}${mantissa.slice(0, point)}.${mantissa.slice(point)}`;
}

function padFraction(text: string, minDecimals: number): string {
  const [integer, fraction = ''] = text.split('.');
  if (fraction.length >= minDecimals) return text;
  return `${integer}.${fraction.padEnd(minDecimals, '0')}`;
}

/**
 * Presentation-only formatter for the clinical interface. Returns null for non-finite
 * values so the caller shows its own "not specified" text instead of a number.
 * - Comma is the only decimal separator; no thousands separators; independent of locale.
 * - Without maxDecimals the value is shown with full (shortest round-trip) precision.
 * - maxDecimals rounds the display only. A non-zero value is never shown as zero: if
 *   rounding would hide it, full precision is shown instead.
 */
export function formatClinicalNumber(value: number, opts: ClinicalFormatOptions = {}): string | null {
  if (!Number.isFinite(value)) return null;
  const min = digits(opts.minDecimals, 0);
  const max = digits(opts.maxDecimals, MAX_DECIMALS);
  if (min > max) throw new RangeError('minDecimals cannot exceed maxDecimals');
  const normalized = Object.is(value, -0) ? 0 : value;
  let text = padFraction(plainDecimal(normalized), min);
  if (opts.maxDecimals !== undefined) {
    // Fixed 'en-US' without grouping: '.' is the only separator it can emit.
    const rounded = new Intl.NumberFormat('en-US', {
      useGrouping: false,
      minimumFractionDigits: min,
      maximumFractionDigits: max,
    }).format(normalized);
    if (normalized === 0 || !/^-?0(\.0*)?$/.test(rounded)) text = rounded;
  }
  return text.replace('.', CLINICAL_DECIMAL_SEPARATOR);
}
