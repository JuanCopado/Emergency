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

/** Canonical finite input: decimal point, optional sign/exponent, no grouping. */
export function parseFiniteDecimal(input: string): number | null {
  const text = input.trim();
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text)) return null;
  const value = Number(text);
  return Number.isFinite(value) ? value : null;
}

/** Non-negative infusion input. A comma is rejected, never silently reinterpreted. */
export function parseDecimal(input: string): number | null {
  const text = input.trim();
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(text)) return null;
  return parseFiniteDecimal(text);
}
