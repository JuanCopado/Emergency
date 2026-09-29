import { describe, expect, it } from 'vitest';
import { db, drugs } from '../data';
import pyExpected from './__fixtures__/python-expected.json';
import {
  InfusionError,
  buildTitrationTable,
  computeBolus,
  concentrationFromAmount,
  convertConcentration,
  convertDose,
  doseToRate,
  rateToDose,
  roundForDisplay,
  roundTo,
  symbolicFormula,
} from './infusion';

describe('data file', () => {
  it('parses against the zod schema with 17 drugs, all draft', () => {
    expect(drugs).toHaveLength(17);
    expect(new Set(drugs.map((d) => d.reviewStatus))).toEqual(new Set(['draft-pending-clinical-review']));
    expect(db.meta.contentVersion).toBe('v1.35');
  });

  it('preparation concentrations equal amount / final volume when both are stated', () => {
    for (const d of drugs) {
      for (const p of d.preparations) {
        if (!p.amount || !p.finalVolumeMl) continue;
        const c = concentrationFromAmount(p.amount.value, p.amount.unit, p.finalVolumeMl);
        const conv = convertConcentration(c, p.concentration.unit.split('/')[0] as 'mcg');
        expect(conv.value, `${d.id}/${p.id}`).toBeCloseTo(p.concentration.value, 9);
      }
    }
  });
});

describe('worked 70 kg examples from the v1.35 modules', () => {
  const cases = drugs.flatMap((d) => d.workedExamples.map((w) => ({ drug: d, w })));
  it.each(cases.map((c) => [`${c.drug.id} ${c.w.dose} ${c.w.doseUnit} @ ${c.w.preparationId}`, c] as const))(
    '%s',
    (_label, { drug, w }) => {
      const prep = drug.preparations.find((p) => p.id === w.preparationId)!;
      const r = doseToRate({ dose: w.dose, doseUnit: w.doseUnit, concentration: prep.concentration, weightKg: w.weightKg });
      expect(r.status).toBe('ok');
      if (r.status !== 'ok') return;
      // Module values are either exact or already rounded to 0.1 mL/h.
      const decimals = (String(w.expectedMlH).split('.')[1] ?? '').length;
      expect(roundTo(r.mlPerHour, Math.max(decimals, 1))).toBeCloseTo(w.expectedMlH, 9);
      expect(r.mlPerHourDisplay).toBe(roundForDisplay(w.expectedMlH));
    },
  );

  it('covers all worked examples (34)', () => {
    expect(cases).toHaveLength(34);
  });

  it('norepinephrine 0.05 mcg/kg/min at 40 mcg/mL, 70 kg = 5.25 mL/h (display 5.3) with arithmetic steps', () => {
    const r = doseToRate({ dose: 0.05, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' }, weightKg: 70 });
    if (r.status !== 'ok') throw new Error('expected ok');
    expect(r.mlPerHour).toBeCloseTo(5.25, 12);
    expect(r.mlPerHourDisplay).toBe(5.3);
    expect(r.amountPerHour).toBeCloseTo(210, 12);
    expect(r.steps.map((s) => s.kind)).toEqual(['weight-multiply', 'per-min-to-per-hour', 'divide-concentration']);
  });

  it('propofol mcg/kg/min against mg/mL converts units (5 mcg/kg/min → 21 mg/h → 2.1 mL/h)', () => {
    const r = doseToRate({ dose: 5, doseUnit: 'mcg/kg/min', concentration: { value: 10, unit: 'mg/mL' }, weightKg: 70 });
    if (r.status !== 'ok') throw new Error('expected ok');
    expect(r.amountPerHour).toBeCloseTo(21, 12);
    expect(r.amountUnit).toBe('mg');
    expect(r.mlPerHour).toBeCloseTo(2.1, 12);
    expect(r.steps.some((s) => s.kind === 'convert-amount')).toBe(true);
  });
});

describe('cross-check with v1.35 scripts/infusion_calculator.py', () => {
  it.each(pyExpected.cases.map((c) => [`${c.drug} ${c.dose} ${c.doseUnit} (${c.method})`, c] as const))('%s', (_l, c) => {
    const drug = drugs.find((d) => d.id === c.drug)!;
    const prep = drug.preparations.find((p) => p.id === c.preparationId)!;
    const r = doseToRate({
      dose: c.dose,
      doseUnit: c.doseUnit as never,
      concentration: prep.concentration,
      weightKg: c.weightKg,
    });
    if (r.status !== 'ok') throw new Error('expected ok');
    expect(Math.abs(r.mlPerHour - c.mlPerHour)).toBeLessThan(1e-9);
  });
});

describe('all supported dose units', () => {
  const w = 70;
  it.each([
    ['mcg/kg/min', 0.1, { value: 40, unit: 'mcg/mL' }, 10.5],
    ['mcg/kg/h', 0.7, { value: 4, unit: 'mcg/mL' }, 12.25],
    ['mg/kg/h', 0.1, { value: 1, unit: 'mg/mL' }, 7],
    ['mcg/min', 20, { value: 20, unit: 'mcg/mL' }, 60],
    ['mg/h', 0.5, { value: 0.1, unit: 'mg/mL' }, 5],
    ['units/min', 0.03, { value: 1, unit: 'units/mL' }, 1.8],
    ['units/h', 1.8, { value: 1, unit: 'units/mL' }, 1.8],
    ['ng/kg/min', 20, { value: 10000, unit: 'ng/mL' }, 8.4],
    ['ng/kg/min', 20, { value: 0.01, unit: 'mg/mL' }, 8.4],
    ['mcg/min', 12, { value: 0.04, unit: 'mg/mL' }, 18],
  ] as const)('%s %d → %o', (unit, dose, conc, expected) => {
    const r = doseToRate({ dose, doseUnit: unit, concentration: conc, weightKg: w });
    if (r.status !== 'ok') throw new Error('expected ok');
    expect(r.mlPerHour).toBeCloseTo(expected, 9);
    const back = rateToDose({ mlPerHour: r.mlPerHour, doseUnit: unit, concentration: conc, weightKg: w });
    if (back.status !== 'ok') throw new Error('expected ok');
    expect(back.dose).toBeCloseTo(dose, 9);
  });
});

describe('reverse (mL/h → dose)', () => {
  it('10.5 mL/h of 40 mcg/mL at 70 kg = 0.1 mcg/kg/min', () => {
    const r = rateToDose({ mlPerHour: 10.5, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' }, weightKg: 70 });
    expect(r.status === 'ok' && r.dose).toBeCloseTo(0.1, 12);
  });
  it('needs weight for weight-based reverse', () => {
    const r = rateToDose({ mlPerHour: 5, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' } });
    expect(r.status).toBe('needs-weight');
  });
});

describe('validation', () => {
  it('missing weight → no patient-specific rate, symbolic formula instead', () => {
    const r = doseToRate({ dose: 0.05, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' }, weightKg: null });
    expect(r).toEqual({ status: 'needs-weight', formula: 'mL/h = dose (mcg/kg/min) × weight (kg) × 60 ÷ concentration (mcg/mL)' });
  });
  it('fixed-dose drugs do not need weight', () => {
    const r = doseToRate({ dose: 0.03, doseUnit: 'units/min', concentration: { value: 1, unit: 'units/mL' } });
    expect(r.status).toBe('ok');
  });
  it('rejects zero/negative/NaN inputs', () => {
    const conc = { value: 40, unit: 'mcg/mL' } as const;
    expect(() => doseToRate({ dose: 0, doseUnit: 'mcg/kg/min', concentration: conc, weightKg: 70 })).toThrow(InfusionError);
    expect(() => doseToRate({ dose: -1, doseUnit: 'mcg/kg/min', concentration: conc, weightKg: 70 })).toThrow(InfusionError);
    expect(() => doseToRate({ dose: NaN, doseUnit: 'mcg/kg/min', concentration: conc, weightKg: 70 })).toThrow(InfusionError);
    expect(() => doseToRate({ dose: 1, doseUnit: 'mcg/kg/min', concentration: conc, weightKg: 0 })).toThrow(/Weight/);
    expect(() => doseToRate({ dose: 1, doseUnit: 'mcg/kg/min', concentration: { value: 0, unit: 'mcg/mL' }, weightKg: 70 })).toThrow(/Concentration/);
    expect(() => concentrationFromAmount(8, 'mg', 0)).toThrow(InfusionError);
    expect(() => rateToDose({ mlPerHour: 0, doseUnit: 'mg/h', concentration: { value: 1, unit: 'mg/mL' } })).toThrow(InfusionError);
  });
  it('rejects mass ↔ units mismatch', () => {
    expect(() => doseToRate({ dose: 1, doseUnit: 'units/min', concentration: { value: 40, unit: 'mcg/mL' } })).toThrow(/incompatible/);
  });
  it('symbolic formulas by unit family', () => {
    expect(symbolicFormula('mg/h', 'mg/mL')).toBe('mL/h = dose (mg/h) ÷ concentration (mg/mL)');
    expect(symbolicFormula('mcg/kg/h', 'mcg/mL')).toBe('mL/h = dose (mcg/kg/h) × weight (kg) ÷ concentration (mcg/mL)');
  });
});

describe('helpers', () => {
  it('concentration from amount/volume', () => {
    expect(concentrationFromAmount(8, 'mg', 200)).toEqual({ value: 0.04, unit: 'mg/mL' });
    expect(convertConcentration(concentrationFromAmount(8, 'mg', 200), 'mcg').value).toBeCloseTo(40, 12);
  });
  it('rounds half up for display, keeps precision otherwise', () => {
    expect(roundForDisplay(5.25)).toBe(5.3);
    expect(roundForDisplay(2.625)).toBe(2.6);
    expect(roundForDisplay(13.125)).toBe(13.1);
    expect(roundForDisplay(7.875)).toBe(7.9);
    expect(roundForDisplay(12.25)).toBe(12.3);
    expect(roundTo(1.005, 2)).toBe(1.01);
  });
  it('converts doses between units', () => {
    expect(convertDose(4, 'mg/kg/h', 'mcg/kg/min')).toBeCloseTo(66.6667, 3);
    expect(convertDose(5, 'mcg/kg/min', 'mg/kg/h')).toBeCloseTo(0.3, 12);
    expect(convertDose(0.4, 'mg/h', 'mcg/min')).toBeCloseTo(6.6667, 3);
    expect(convertDose(0.05, 'mcg/kg/min', 'mcg/min', 70)).toBeCloseTo(3.5, 12);
    expect(() => convertDose(0.05, 'mcg/kg/min', 'mcg/min')).toThrow();
  });
  it('titration table', () => {
    const rows = buildTitrationTable({ from: 0.05, to: 0.25, step: 0.05, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' }, weightKg: 70 });
    expect(rows?.map((r) => r.dose)).toEqual([0.05, 0.1, 0.15, 0.2, 0.25]);
    expect(rows?.map((r) => r.mlPerHourDisplay)).toEqual([5.3, 10.5, 15.8, 21, 26.3]);
    expect(buildTitrationTable({ from: 0.05, to: 0.25, step: 0.05, doseUnit: 'mcg/kg/min', concentration: { value: 40, unit: 'mcg/mL' } })).toBeNull();
    const vp = buildTitrationTable({ from: 0.01, to: 0.07, step: 0.005, doseUnit: 'units/min', concentration: { value: 1, unit: 'units/mL' } });
    expect(vp).toHaveLength(13);
    expect(vp?.[0]?.mlPerHourDisplay).toBe(0.6);
    expect(vp?.at(-1)?.mlPerHourDisplay).toBe(4.2);
  });
});

describe('bolus / loading (dose, volume, time — never mL/h)', () => {
  const bolusCases = drugs.flatMap((d) => d.bolusExamples.map((b) => ({ d, b })));
  it.each(bolusCases.map((c) => [c.d.id, c] as const))('%s module example', (_id, { d, b }) => {
    const prep = b.preparationId ? d.preparations.find((p) => p.id === b.preparationId) : null;
    const r = computeBolus({ dosePerKg: b.dosePerKg, unit: b.unit, weightKg: b.weightKg, concentration: prep?.concentration ?? null, durationMin: b.durationMin });
    expect(r.amount).toBeCloseTo(b.expectedAmount, 9);
    expect(r.amountUnit).toBe(b.expectedAmountUnit);
    if (b.expectedVolumeMl !== null) expect(r.volumeMl).toBeCloseTo(b.expectedVolumeMl, 9);
    expect(r.durationMin).toBe(b.durationMin);
    expect(Object.keys(r)).not.toContain('mlPerHour');
  });
});
