import type { PediatricReport } from './PediatricExport';
import generated from '../data/generatedPediatricOutpatient.json';
import { parseClinicalNumber } from '../lib/clinicalInput';

export type Value = string | number | boolean | null | Value[] | { [key: string]: Value };
export type Fields = { [key: string]: Value };
export type Gate = { field: string; message?: string; equals?: boolean; drug?: string; minimum?: number; maximum?: number };
export type Regimen = Fields & {
  id: string; drug_id: string; drug: string; diagnosis: string; route: string; weight_basis: string;
  required_patient_flags?: Gate[]; excluded_patient_flags?: Gate[];
  minimum_patient_values?: Gate[]; maximum_patient_values?: Gate[];
};
type Catalog = {
  source_revision: string; status: string; regimens: Regimen[];
  drugs: { id: string; name: string; components: string[] }[];
  condition_rules: Gate[];
  inventory: { regimens: number; drug_groups: number; diagnoses: number };
};
export const pediatricCatalog = generated as unknown as Catalog;
export const findRegimen = (id: string) => pediatricCatalog.regimens.find((r) => r.id === id);
export const regimensForDrug = (id: string) => pediatricCatalog.regimens.filter((r) => r.drug_id === id);

export type Safety = { prescription_status: string; alerts: { severity: string; message: string; action: string }[] };
export type Calculation = { blocked: boolean; export_report?: PediatricReport; result?: Fields; safety: Safety };

export async function calculatePediatric(body: Fields): Promise<Calculation> {
  const base = (import.meta.env.VITE_CLINICAL_NOTE_API_BASE ?? '').replace(/\/$/, '');
  const response = await fetch(`${base}/api/pediatric-outpatient/calculate`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, cache: 'no-store',
    body: JSON.stringify({ ...body, source_revision: pediatricCatalog.source_revision }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'No se pudo calcular la pauta');
  return result as Calculation;
}

export function numericInput(text: string, label: string, allowZero = false): number {
  // Approved decimal policy: comma is the only decimal separator; the returned number is ordinary.
  const parsed = parseClinicalNumber(text, { allowNegative: false });
  if (!parsed.ok && /^\s*\d+\.\d+\s*$/.test(text)) {
    throw new Error(`${label}: usa coma como separador decimal (p. ej. 12,5), no punto`);
  }
  const n = parsed.ok ? parsed.value : Number.NaN;
  if (!Number.isFinite(n) || (allowZero ? n < 0 : n <= 0)) {
    throw new Error(`${label}: introduce un número finito ${allowZero ? 'mayor o igual que cero' : 'mayor que cero'}, sin signo, exponente ni unidades; decimales con coma`);
  }
  return n;
}
