import { isWeightBased } from '../data';
import type { Drug } from '../data/schema';

export type DoseFilter = 'all' | 'weight' | 'fixed';

export function filterDrugs(list: readonly Drug[], opts: { q: string; category: string; dose: DoseFilter; localName: (d: Drug) => string }) {
  const q = opts.q.trim().toLowerCase();
  return list
    .filter((d) => opts.category === 'all' || d.category === opts.category)
    .filter((d) => opts.dose === 'all' || (opts.dose === 'weight') === isWeightBased(d))
    .filter((d) => !q || [d.name, d.id, ...d.synonyms, opts.localName(d)].some((s) => s.toLowerCase().includes(q)))
    .sort((a, b) => a.name.localeCompare(b.name));
}
