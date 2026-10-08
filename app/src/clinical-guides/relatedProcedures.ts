import procedures from '../data/generatedProcedures.json';
import type { CanonicalGuide } from './canonical';

export type RelatedProcedure = {
  id: string;
  name: string;
  level: string;
  family: string;
};

const ALL = procedures as RelatedProcedure[];
const STOP = new Set(['de','del','la','el','los','las','y','en','con','por','para','un','una','the','and','of','to','with','acute','emergency','emergencies']);

const normalize = (value: string) =>
  value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

const tokens = (value: string) =>
  new Set(normalize(value).split(/[^a-z0-9]+/).filter((token) => token.length > 3 && !STOP.has(token)));

const PREFIX_HINTS: Array<[RegExp, string[]]> = [
  [/airway|respirat|asthma|copd|oxygen|ventilat|bronchiol|croup/, ['PROC-AIR-', 'PROC-THX-']],
  [/cardiac|cardio|arrhythm|arrest|coronary|heart|tampon|aortic|valv|syncope|shock/, ['PROC-CV-', 'PROC-VASC-']],
  [/trauma|hemorrhage|bleeding|burn|wound|soft-tissue/, ['PROC-TRA-', 'PROC-WND-']],
  [/orthopedic|musculoskeletal|fracture|joint|dislocation/, ['PROC-ORTHO-', 'PROC-WND-']],
  [/neurolog|stroke|seizure|epilep|headache|intracran|spinal|consciousness|coma/, ['PROC-NEURO-']],
  [/gastro|abdomen|abdominal|pancreat|liver|gi-|mesenteric/, ['PROC-GI-']],
  [/renal|urolog|bladder|priap|paraphim/, ['PROC-GU-']],
  [/ophthalm|ocular|eye/, ['PROC-EYE-']],
  [/ent-|ear|nasal|epistaxis|dental|mandib/, ['PROC-ENT-']],
  [/pediatric|paediatric|child|infant|neonat/, ['PROC-PED-']],
  [/obstetric|pregnan|postpartum|eclamp/, ['PROC-OB-']],
  [/pocus|ultrasound|echo/, ['PROC-US-']],
  [/toxic|environment|hypotherm|drowning/, ['PROC-SP-']],
];

export function getRelatedProcedures(guide: CanonicalGuide, limit = 8): RelatedProcedure[] {
  const haystack = normalize([guide.id, guide.title, guide.body].join(' '));
  const sourceTokens = tokens(haystack);
  const hinted = new Set<string>();
  for (const [pattern, prefixes] of PREFIX_HINTS) {
    if (pattern.test(haystack)) prefixes.forEach((prefix) => hinted.add(prefix));
  }

  return ALL
    .map((procedure) => {
      const procedureTokens = tokens([procedure.name, procedure.family].join(' '));
      let score = 0;
      for (const token of procedureTokens) if (sourceTokens.has(token)) score += 3;
      if ([...hinted].some((prefix) => procedure.id.startsWith(prefix))) score += 4;
      if (haystack.includes(normalize(procedure.name))) score += 8;
      return { procedure, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || a.procedure.id.localeCompare(b.procedure.id))
    .slice(0, limit)
    .map(({ procedure }) => procedure);
}
