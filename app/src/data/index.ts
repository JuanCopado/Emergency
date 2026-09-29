import raw from './drugs.json';
import { drugDatabaseSchema, type Drug, type DrugDatabase, type Preparation } from './schema';

/** Validated at module load; a malformed data file fails fast (and in tests). */
export const db: DrugDatabase = drugDatabaseSchema.parse(raw);
export const drugs: readonly Drug[] = db.drugs;

export function getDrug(id: string | undefined | null): Drug | undefined {
  return id ? drugs.find((d) => d.id === id) : undefined;
}

export function getModule(id: string) {
  return db.modules[id];
}

export function defaultPreparation(drug: Drug): Preparation {
  return drug.preparations.find((p) => p.isDefault) ?? (drug.preparations[0] as Preparation);
}

export function isWeightBased(drug: Drug): boolean {
  return drug.doseUnit.includes('/kg/');
}

export function searchDrugs(query: string, list: readonly Drug[] = drugs): Drug[] {
  const q = query.trim().toLowerCase();
  if (!q) return [...list];
  return list.filter((d) => [d.name, d.id, ...d.synonyms].some((s) => s.toLowerCase().includes(q)));
}
