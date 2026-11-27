import { describe, expect, it } from 'vitest';
import {
  compareCorticosteroids, corticosteroidCatalog, formatCorticosteroidNumber, parseCorticosteroidDose,
  CorticosteroidCalculationError, type ComparisonRequest,
} from './calculator';

const request = (overrides: Partial<ComparisonRequest> = {}): ComparisonRequest => ({
  tableId: 'endotext-2018', sourceDrugId: 'hydrocortisone', doseMg: '20', route: 'iv', doseBasis: 'daily_total', ...overrides,
});
const amount = (input: ComparisonRequest, id: string) =>
  compareCorticosteroids(input).rows.find(row => row.drugId === id)!.approximateMg;

describe('source-attributed systemic equivalence', () => {
  it('retains the published Endotext reference independently of the ESE table', () => {
    const expected = { hydrocortisone: 20, cortisone: 25, prednisone: 5, prednisolone: 5, methylprednisolone: 4, triamcinolone: 4, dexamethasone: 0.75, betamethasone: 0.6 };
    const output = compareCorticosteroids(request());
    expect(Object.fromEntries(output.rows.map(row => [row.drugId, row.approximateMg]))).toEqual(expected);
    expect(output.sourceId).toBe('endotext-2018');
    expect(output.doseBasis).toBe('daily_total');
  });
  it('uses ESE 2024 dexamethasone and betamethasone 0.5 mg without mixing durations', () => {
    const output = compareCorticosteroids(request({ tableId: 'ese-es-2024' }));
    expect(output.rows.find(row => row.drugId === 'dexamethasone')).toMatchObject({ approximateMg: 0.5, biologicalHalfLifeHours: [36, 72] });
    expect(output.rows.find(row => row.drugId === 'betamethasone')?.approximateMg).toBe(0.5);
    expect(output.sourceId).toBe('ese-es-2024');
  });
  it('converts an independently specified dexamethasone dose and preserves a single-dose basis', () => {
    expect(amount(request({ sourceDrugId: 'dexamethasone', doseMg: '0.75', doseBasis: 'single_dose' }), 'hydrocortisone')).toBe(20);
    expect(amount(request({ tableId: 'ese-es-2024', sourceDrugId: 'dexamethasone', doseMg: '0.75' }), 'hydrocortisone')).toBe(30);
    expect(amount(request({ sourceDrugId: 'prednisone', doseMg: '40', route: 'oral' }), 'methylprednisolone')).toBe(32);
  });
  it.each(['', ' ', '0', '-0', '-1', 'NaN', 'Infinity', '1e309', '1e-9999', '0x10', '1,5', '1,000', '1_000', '20 mg', 'false'])('rejects invalid or ambiguous dose %s', doseMg => {
    expect(() => compareCorticosteroids(request({ doseMg }))).toThrow(CorticosteroidCalculationError);
  });
  it.each([null, false, [], {}, 20])('rejects non-string coercions %j', value => {
    expect(() => parseCorticosteroidDose(value)).toThrow(CorticosteroidCalculationError);
  });
  it('rejects unsupported routes and missing source/basis instead of applying defaults', () => {
    for (const route of ['topical', 'inhaled', 'im', 'depot', '']) expect(() => compareCorticosteroids(request({ route }))).toThrow('unsupported_route');
    expect(() => compareCorticosteroids(request({ tableId: '' }))).toThrow('source_required');
    expect(() => compareCorticosteroids(request({ sourceDrugId: 'unknown' }))).toThrow('drug_required');
    expect(() => compareCorticosteroids(request({ doseBasis: '' }))).toThrow('basis_required');
  });
  it('rejects output overflow and positive output lost to zero', () => {
    expect(() => compareCorticosteroids(request({ sourceDrugId: 'dexamethasone', doseMg: '1e308' }))).toThrow('unrepresentable');
    expect(() => compareCorticosteroids(request({ doseMg: '5e-324' }))).toThrow('unrepresentable');
  });
  it('does not round a representable small positive result to zero in any UI locale', () => {
    const value = amount(request({ doseMg: '0.000001' }), 'dexamethasone');
    expect(value).toBeGreaterThan(0);
    for (const locale of ['es', 'pt', 'en', 'zh']) expect(formatCorticosteroidNumber(value, locale)).not.toMatch(/^0(?:[.,]0+)?$/);
  });
  it('keeps pediatric adrenal crisis separate from the adult maintenance regimen', () => {
    const hydrocortisone = corticosteroidCatalog.hydrocortisone;
    expect(hydrocortisone.adult_adrenal_crisis.maintenance_alternative_mg).toBe(50);
    expect(hydrocortisone.pediatric_adrenal_crisis.rows.at(-1)?.maintenance_mg).toEqual([25, 25]);
    expect(hydrocortisone.pediatric_adrenal_crisis.rows[2]?.maintenance_mg).toEqual([12.5, 12.5]);
    expect(hydrocortisone.pediatric_adrenal_crisis.source_ids).toEqual(['rch-adrenal-2024']);
    expect(hydrocortisone.pediatric_septic_shock.source_ids).toEqual(['ssc-pediatric-2026']);
  });
});
