import type { Drug } from '../data/schema';

/** Round a raw step to a "nice" 1/2/2.5/5 × 10^n value. */
export function niceStep(raw: number): number {
  if (!(raw > 0) || !Number.isFinite(raw)) return 1;
  const exp = Math.floor(Math.log10(raw));
  const base = 10 ** exp;
  const f = raw / base;
  const nice = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
  return Number((nice * base).toPrecision(6));
}

/**
 * Default reference-table bounds derived from the drug record (start/range/max/titration step).
 * These are presentation defaults for a clearly labelled reference table, not recommendations.
 */
export function titrationDefaults(drug: Drug): { from: number; to: number; step: number } {
  const d = drug.dosing;
  const from = d.start?.min ?? d.range?.min ?? drug.workedExamples[0]?.dose ?? 1;
  let to = d.max?.value ?? d.range?.max ?? from * 10;
  if (to <= from) to = from * 10;
  let step = d.titration?.stepMin ?? niceStep((to - from) / 10);
  if ((to - from) / step > 30) step = niceStep((to - from) / 20);
  return { from, to, step };
}
