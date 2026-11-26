import generated from './catalog.generated.json';
import type { CorticosteroidCatalog, CorticosteroidLocale, DoseBasis, SystemicRoute } from './types';

export const corticosteroidCatalog = generated as CorticosteroidCatalog;
export type CorticosteroidErrorCode = 'source_required' | 'drug_required' | 'invalid_dose' | 'unsupported_route' | 'basis_required' | 'unrepresentable';
export class CorticosteroidCalculationError extends Error {
  constructor(public readonly code: CorticosteroidErrorCode) {
    super(code);
    this.name = 'CorticosteroidCalculationError';
  }
}
export interface ComparisonRequest {
  tableId: string;
  sourceDrugId: string;
  doseMg: string;
  route: string;
  doseBasis: string;
}
export interface ConversionResult {
  drugId: string;
  approximateMg: number;
  referenceEquivalentMg: number;
  biologicalHalfLifeHours: [number, number];
}
export interface ComparisonResult {
  tableId: string;
  sourceId: string;
  catalogVersion: string;
  sourceDrugId: string;
  inputMg: number;
  sourceEquivalentMg: number;
  route: SystemicRoute;
  doseBasis: DoseBasis;
  rows: ConversionResult[];
}

/** Parse the shared point-decimal/no-grouping contract without accepting JS coercions. */
export function parseCorticosteroidDose(raw: unknown): number {
  if (typeof raw !== 'string') throw new CorticosteroidCalculationError('invalid_dose');
  const text = raw.trim();
  if (!text || text.length > 64 || !/^(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(text)) {
    throw new CorticosteroidCalculationError('invalid_dose');
  }
  const dose = Number(text);
  // This rejects zero, negative zero, nonfinite inputs, and nonzero mantissas lost to zero.
  if (!Number.isFinite(dose) || dose <= 0) throw new CorticosteroidCalculationError('invalid_dose');
  return dose;
}

/** One selected source, same dose basis. This never selects treatment, frequency or a pediatric dose. */
export function compareCorticosteroids(input: ComparisonRequest): ComparisonResult {
  const table = corticosteroidCatalog.tables.find(row => row.id === input.tableId);
  if (!table) throw new CorticosteroidCalculationError('source_required');
  const from = table.rows.find(row => row.drug_id === input.sourceDrugId);
  if (!from) throw new CorticosteroidCalculationError('drug_required');
  if (input.route !== 'oral' && input.route !== 'iv') throw new CorticosteroidCalculationError('unsupported_route');
  if (input.doseBasis !== 'single_dose' && input.doseBasis !== 'daily_total') throw new CorticosteroidCalculationError('basis_required');
  const dose = parseCorticosteroidDose(input.doseMg);
  const rows = table.rows.map(row => {
    const approximateMg = dose * (row.equivalent_mg / from.equivalent_mg);
    // No Infinity or positive dose rounded by IEEE-754 to zero can be rendered as a valid comparison.
    if (!Number.isFinite(approximateMg) || approximateMg <= 0) {
      throw new CorticosteroidCalculationError('unrepresentable');
    }
    return { drugId: row.drug_id, approximateMg, referenceEquivalentMg: row.equivalent_mg,
      biologicalHalfLifeHours: row.biological_half_life_hours };
  });
  return { tableId: table.id, sourceId: table.source_id, catalogVersion: corticosteroidCatalog.version,
    sourceDrugId: from.drug_id, inputMg: dose, sourceEquivalentMg: from.equivalent_mg,
    route: input.route, doseBasis: input.doseBasis, rows };
}

export function corticosteroidLocale(language: string): CorticosteroidLocale {
  const candidate = language.toLowerCase().split('-')[0];
  return candidate === 'es' || candidate === 'pt' || candidate === 'zh' ? candidate : 'en';
}

/** Significant digits prevent a small positive result from being displayed as a zero dose. */
export function formatCorticosteroidNumber(value: number, language: string): string {
  const locale = corticosteroidLocale(language);
  return new Intl.NumberFormat(locale, {
    maximumSignificantDigits: 10,
    useGrouping: false,
    notation: value !== 0 && (Math.abs(value) < 0.0001 || Math.abs(value) >= 1e9) ? 'scientific' : 'standard',
  }).format(value);
}
