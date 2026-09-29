/**
 * Infusion arithmetic engine.
 *
 * Pure functions, no UI. All internal arithmetic keeps full floating precision;
 * rounding is applied only for display (`roundForDisplay`, default 0.1 mL/h).
 *
 * Formulas (module `medication-selection-safety` / `vasoactive-inotrope-infusions`):
 *   weight-based per minute: mL/h = dose (x/kg/min) × kg × 60 ÷ concentration (x/mL)
 *   weight-based per hour:   mL/h = dose (x/kg/h)   × kg      ÷ concentration (x/mL)
 *   fixed per minute:        mL/h = dose (x/min)    × 60      ÷ concentration (x/mL)
 *   fixed per hour:          mL/h = dose (x/h)                ÷ concentration (x/mL)
 */
import type { AmountUnit, ConcentrationUnit, DoseUnit } from '../data/schema';

export type MassUnit = 'ng' | 'mcg' | 'mg';
export type TimeBase = 'min' | 'h';

export interface ParsedDoseUnit {
  amount: AmountUnit;
  perKg: boolean;
  time: TimeBase;
}

/** Mass factors expressed in nanograms. `units` is a separate (non-mass) dimension. */
const NG_PER: Record<MassUnit, number> = { ng: 1, mcg: 1_000, mg: 1_000_000 };

export function parseDoseUnit(unit: DoseUnit): ParsedDoseUnit {
  const parts = unit.split('/');
  const amount = parts[0] as AmountUnit;
  const perKg = parts.length === 3 && parts[1] === 'kg';
  const time = parts[parts.length - 1] as TimeBase;
  return { amount, perKg, time };
}

export function concentrationAmountUnit(unit: ConcentrationUnit): AmountUnit {
  return unit.split('/')[0] as AmountUnit;
}

export function isWeightBasedUnit(unit: DoseUnit): boolean {
  return parseDoseUnit(unit).perKg;
}

/** Factor converting an amount in `from` to `to` (e.g. mg→mcg = 1000). Throws if incompatible. */
export function amountFactor(from: AmountUnit, to: AmountUnit): number {
  if (from === to) return 1;
  if (from === 'units' || to === 'units') {
    throw new InfusionError('incompatible-units', `Cannot convert ${from} to ${to}`);
  }
  return NG_PER[from] / NG_PER[to];
}

export function unitsCompatible(dose: DoseUnit, conc: ConcentrationUnit): boolean {
  const a = parseDoseUnit(dose).amount;
  const b = concentrationAmountUnit(conc);
  return (a === 'units') === (b === 'units');
}

export class InfusionError extends Error {
  constructor(
    public readonly code:
      | 'incompatible-units'
      | 'invalid-dose'
      | 'invalid-concentration'
      | 'invalid-weight'
      | 'invalid-rate'
      | 'invalid-volume'
      | 'invalid-amount',
    message: string,
  ) {
    super(message);
    this.name = 'InfusionError';
  }
}

export interface Concentration {
  value: number;
  unit: ConcentrationUnit;
}

/** Final concentration from a drug amount diluted to a final volume. Keeps the amount unit. */
export function concentrationFromAmount(amount: number, amountUnit: AmountUnit, finalVolumeMl: number): Concentration {
  if (!isPositiveFinite(amount)) throw new InfusionError('invalid-amount', 'Drug amount must be > 0');
  if (!isPositiveFinite(finalVolumeMl)) throw new InfusionError('invalid-volume', 'Final volume must be > 0');
  return { value: amount / finalVolumeMl, unit: `${amountUnit}/mL` as ConcentrationUnit };
}

/** Express a concentration in another amount unit (e.g. 1 mg/mL → 1000 mcg/mL). */
export function convertConcentration(c: Concentration, to: AmountUnit): Concentration {
  const from = concentrationAmountUnit(c.unit);
  return { value: c.value * amountFactor(from, to), unit: `${to}/mL` as ConcentrationUnit };
}

export function isPositiveFinite(n: unknown): n is number {
  return typeof n === 'number' && Number.isFinite(n) && n > 0;
}

/** Round half away from zero with an epsilon guard (5.25 → 5.3, 2.625 → 2.6). */
export function roundTo(value: number, decimals = 1): number {
  const f = 10 ** decimals;
  const r = Math.round((Math.abs(value) + Number.EPSILON * Math.max(1, Math.abs(value))) * f) / f;
  return Math.sign(value) * r;
}

export const DISPLAY_DECIMALS_ML_H = 1;
export function roundForDisplay(mlPerHour: number): number {
  return roundTo(mlPerHour, DISPLAY_DECIMALS_ML_H);
}

/** Structured arithmetic step; the UI renders/translates these. */
export type CalcStep =
  | { kind: 'weight-multiply'; dose: number; doseUnit: DoseUnit; weightKg: number; result: number; resultUnit: string }
  | { kind: 'per-min-to-per-hour'; value: number; valueUnit: string; result: number; resultUnit: string }
  | { kind: 'convert-amount'; value: number; from: AmountUnit; to: AmountUnit; factor: number; result: number }
  | { kind: 'divide-concentration'; amountPerHour: number; amountUnit: AmountUnit; concentration: number; concentrationUnit: ConcentrationUnit; result: number };

export interface ForwardInput {
  dose: number;
  doseUnit: DoseUnit;
  concentration: Concentration;
  weightKg?: number | null;
}

export type ForwardResult =
  | {
      status: 'ok';
      mlPerHour: number;
      mlPerHourDisplay: number;
      amountPerHour: number;
      amountUnit: AmountUnit;
      steps: CalcStep[];
      formula: string;
    }
  | { status: 'needs-weight'; formula: string };

/** Human-readable symbolic formula for a dose unit (shown when weight is missing). */
export function symbolicFormula(doseUnit: DoseUnit, concUnit: ConcentrationUnit): string {
  const { perKg, time } = parseDoseUnit(doseUnit);
  const parts = [`dose (${doseUnit})`];
  if (perKg) parts.push('weight (kg)');
  if (time === 'min') parts.push('60');
  return `mL/h = ${parts.join(' × ')} ÷ concentration (${concUnit})`;
}

/** Forward calculation: dose → pump rate (mL/h). */
export function doseToRate(input: ForwardInput): ForwardResult {
  const { dose, doseUnit, concentration, weightKg } = input;
  const formula = symbolicFormula(doseUnit, concentration.unit);
  if (!isPositiveFinite(dose)) throw new InfusionError('invalid-dose', 'Dose must be > 0');
  if (!isPositiveFinite(concentration.value)) throw new InfusionError('invalid-concentration', 'Concentration must be > 0');
  if (!unitsCompatible(doseUnit, concentration.unit)) {
    throw new InfusionError('incompatible-units', `${doseUnit} is incompatible with ${concentration.unit}`);
  }
  const parsed = parseDoseUnit(doseUnit);
  if (parsed.perKg && (weightKg === undefined || weightKg === null)) return { status: 'needs-weight', formula };
  if (parsed.perKg && !isPositiveFinite(weightKg)) throw new InfusionError('invalid-weight', 'Weight must be > 0');

  const steps: CalcStep[] = [];
  let value = dose;
  let unitLabel = doseUnit as string;
  if (parsed.perKg) {
    const w = weightKg as number;
    const result = value * w;
    const resultUnit = `${parsed.amount}/${parsed.time}`;
    steps.push({ kind: 'weight-multiply', dose: value, doseUnit, weightKg: w, result, resultUnit });
    value = result;
    unitLabel = resultUnit;
  }
  if (parsed.time === 'min') {
    const result = value * 60;
    const resultUnit = `${parsed.amount}/h`;
    steps.push({ kind: 'per-min-to-per-hour', value, valueUnit: unitLabel, result, resultUnit });
    value = result;
  }
  const concAmount = concentrationAmountUnit(concentration.unit);
  if (concAmount !== parsed.amount) {
    const factor = amountFactor(parsed.amount, concAmount);
    const result = value * factor;
    steps.push({ kind: 'convert-amount', value, from: parsed.amount, to: concAmount, factor, result });
    value = result;
  }
  const mlPerHour = value / concentration.value;
  steps.push({
    kind: 'divide-concentration',
    amountPerHour: value,
    amountUnit: concAmount,
    concentration: concentration.value,
    concentrationUnit: concentration.unit,
    result: mlPerHour,
  });
  return {
    status: 'ok',
    mlPerHour,
    mlPerHourDisplay: roundForDisplay(mlPerHour),
    amountPerHour: value,
    amountUnit: concAmount,
    steps,
    formula,
  };
}

export interface ReverseInput {
  mlPerHour: number;
  doseUnit: DoseUnit;
  concentration: Concentration;
  weightKg?: number | null;
}

export type ReverseResult =
  | { status: 'ok'; dose: number; doseUnit: DoseUnit; amountPerHour: number; amountUnit: AmountUnit }
  | { status: 'needs-weight'; formula: string };

/** Reverse calculation: pump rate (mL/h) → delivered dose in `doseUnit`. */
export function rateToDose(input: ReverseInput): ReverseResult {
  const { mlPerHour, doseUnit, concentration, weightKg } = input;
  if (!isPositiveFinite(mlPerHour)) throw new InfusionError('invalid-rate', 'Rate must be > 0');
  if (!isPositiveFinite(concentration.value)) throw new InfusionError('invalid-concentration', 'Concentration must be > 0');
  if (!unitsCompatible(doseUnit, concentration.unit)) {
    throw new InfusionError('incompatible-units', `${doseUnit} is incompatible with ${concentration.unit}`);
  }
  const parsed = parseDoseUnit(doseUnit);
  if (parsed.perKg && (weightKg === undefined || weightKg === null)) {
    return { status: 'needs-weight', formula: `dose (${doseUnit}) = mL/h × concentration ÷ weight (kg)${parsed.time === 'min' ? ' ÷ 60' : ''}` };
  }
  if (parsed.perKg && !isPositiveFinite(weightKg)) throw new InfusionError('invalid-weight', 'Weight must be > 0');
  const concAmount = concentrationAmountUnit(concentration.unit);
  const amountPerHourConc = mlPerHour * concentration.value;
  const amountPerHour = amountPerHourConc * amountFactor(concAmount, parsed.amount);
  let dose = amountPerHour;
  if (parsed.time === 'min') dose /= 60;
  if (parsed.perKg) dose /= weightKg as number;
  return { status: 'ok', dose, doseUnit, amountPerHour: amountPerHourConc, amountUnit: concAmount };
}

/** Convert a dose value between dose units (weight needed only when crossing per-kg ↔ fixed). */
export function convertDose(value: number, from: DoseUnit, to: DoseUnit, weightKg?: number | null): number {
  const a = parseDoseUnit(from);
  const b = parseDoseUnit(to);
  let v = value * amountFactor(a.amount, b.amount);
  if (a.time === 'min' && b.time === 'h') v *= 60;
  if (a.time === 'h' && b.time === 'min') v /= 60;
  if (a.perKg !== b.perKg) {
    if (!isPositiveFinite(weightKg)) throw new InfusionError('invalid-weight', 'Weight required to convert');
    v = a.perKg ? v * weightKg : v / weightKg;
  }
  return v;
}

export interface TitrationRow {
  dose: number;
  mlPerHour: number;
  mlPerHourDisplay: number;
}

/** Build dose ↔ mL/h rows from `from` to `to` inclusive in `step` increments (max 60 rows). */
export function buildTitrationTable(opts: {
  from: number;
  to: number;
  step: number;
  doseUnit: DoseUnit;
  concentration: Concentration;
  weightKg?: number | null;
}): TitrationRow[] | null {
  const { from, to, step, doseUnit, concentration, weightKg } = opts;
  if (!isPositiveFinite(from) || !isPositiveFinite(to) || !isPositiveFinite(step) || to < from) return [];
  if (isWeightBasedUnit(doseUnit) && !isPositiveFinite(weightKg)) return null;
  const rows: TitrationRow[] = [];
  const n = Math.min(60, Math.floor((to - from) / step + 1e-9));
  for (let i = 0; i <= n; i++) {
    const dose = roundTo(from + i * step, 6);
    const r = doseToRate({ dose, doseUnit, concentration, weightKg });
    if (r.status === 'ok') rows.push({ dose, mlPerHour: r.mlPerHour, mlPerHourDisplay: r.mlPerHourDisplay });
  }
  return rows;
}

export interface BolusResult {
  amount: number;
  amountUnit: MassUnit;
  volumeMl: number | null;
  durationMin: number | null;
}

/**
 * Weight-based bolus/loading dose. Returns dose, volume and time — never mL/h
 * (module rule: do not force bolus medication into mL/h).
 */
export function computeBolus(opts: {
  dosePerKg: number;
  unit: 'mcg/kg' | 'mg/kg';
  weightKg: number;
  concentration?: Concentration | null;
  durationMin?: number | null;
}): BolusResult {
  const { dosePerKg, unit, weightKg, concentration, durationMin } = opts;
  if (!isPositiveFinite(dosePerKg)) throw new InfusionError('invalid-dose', 'Dose must be > 0');
  if (!isPositiveFinite(weightKg)) throw new InfusionError('invalid-weight', 'Weight must be > 0');
  const amountUnit = unit.split('/')[0] as MassUnit;
  const amount = dosePerKg * weightKg;
  let volumeMl: number | null = null;
  if (concentration) {
    const c = convertConcentration(concentration, amountUnit);
    volumeMl = amount / c.value;
  }
  return { amount, amountUnit, volumeMl, durationMin: durationMin ?? null };
}
