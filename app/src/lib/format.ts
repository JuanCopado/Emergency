/** Locale-aware number formatting that never hides clinically relevant decimals. */
export function formatNumber(value: number, locale: string, maxDecimals = 3): string {
  if (!Number.isFinite(value)) return '—';
  return new Intl.NumberFormat(locale, { maximumFractionDigits: maxDecimals, minimumFractionDigits: 0 }).format(value);
}

/** Fixed 1-decimal mL/h display (pump setting). */
export function formatRate(value: number, locale: string): string {
  return new Intl.NumberFormat(locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(value);
}

/** Replace "mcg" with "µg" when the user prefers the SI symbol. */
export function unitLabel(unit: string, micro: 'mcg' | 'µg'): string {
  return micro === 'µg' ? unit.replace(/mcg/g, 'µg') : unit;
}

/** Parse user-entered decimal accepting comma or dot. Returns null on empty/invalid. */
export function parseDecimal(input: string): number | null {
  const s = input.trim().replace(/\s/g, '').replace(',', '.');
  if (!s) return null;
  if (!/^\d*\.?\d+$|^\d+\.$/.test(s)) return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}
