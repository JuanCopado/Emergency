/** Presentation only: never add grouping separators to clinical values. */
export function formatNumber(value: number, locale: string, maxDecimals = 3): string {
  if (!Number.isFinite(value)) return '—';
  return new Intl.NumberFormat(locale, { useGrouping: false, maximumFractionDigits: maxDecimals, minimumFractionDigits: 0 }).format(value);
}

/** Fixed 1-decimal mL/h display (pump setting); arithmetic precision is unchanged. */
export function formatRate(value: number, locale: string): string {
  if (!Number.isFinite(value)) return '—';
  return new Intl.NumberFormat(locale, { useGrouping: false, minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(value);
}

/** Localize a canonical numeric result without rounding or reparsing its display. */
export function formatCanonicalNumber(value: number, locale: string): string {
  if (!Number.isFinite(value)) return '—';
  const decimal = new Intl.NumberFormat(locale).formatToParts(1.1).find(p => p.type === 'decimal')?.value ?? '.';
  return String(value).replace('.', decimal);
}

export function unitLabel(unit: string, micro: 'mcg' | 'µg'): string {
  return micro === 'µg' ? unit.replace(/mcg/g, 'µg') : unit;
}

/** Normalize the magnitude of an already syntax-checked, nonzero decimal.
 * Comparing significant digits and position avoids expanding long exponents. */
function decimalMagnitude(text: string): string {
  const [mantissa = '', exponent = '0'] = text.toLowerCase().split('e');
  const [whole = '', fraction = ''] = mantissa.replace(/^[+-]/, '').split('.');
  const digits = (whole + fraction).replace(/^0+/, '');
  return digits.replace(/0+$/, '') + 'e' + (digits.length - fraction.length + Number(exponent));
}

/** Canonical finite input: decimal point, optional sign/exponent, no grouping. */
export function parseFiniteDecimal(input: string, preserveInteger = false): number | null {
  const text = input.trim();
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text)) return null;
  const value = Number(text);
  // A nonzero mantissa may underflow to zero before case-specific validation.
  if (value === 0 && /[1-9]/.test(text.split(/e/i)[0] ?? '')) return null;
  // For an integer gate verify the decimal the server would actually receive.
  if (preserveInteger && value !== 0 && Number.isInteger(value)
      && decimalMagnitude(text) !== decimalMagnitude(String(value))) return null;
  return Number.isFinite(value) ? value : null;
}

/** Non-negative infusion input. A comma is rejected, never silently reinterpreted. */
export function parseDecimal(input: string): number | null {
  const text = input.trim();
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(text)) return null;
  return parseFiniteDecimal(text);
}
