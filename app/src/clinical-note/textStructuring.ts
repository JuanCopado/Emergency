/**
 * Deterministic, local, lossless structuring of a clinician's own free text.
 *
 * The only operation is to split text at headings the clinician already wrote
 * ("Antecedentes:", "Exploración", "Plan:" ...) in es/pt/en. Nothing is added,
 * translated, inferred or rewritten: every character of the original stays in
 * exactly one section's `raw`, so the original can always be reconstructed.
 * No clinical interpretation, no network, no model.
 */
export type NoteField = 'chief' | 'hpi' | 'pmh' | 'meds' | 'allergies' | 'exam' | 'problems' | 'plan';
export type SectionField = NoteField | 'tests' | 'evolution' | 'unassigned';

export const NOTE_FIELDS: readonly NoteField[] = ['chief', 'hpi', 'pmh', 'meds', 'allergies', 'exam', 'problems', 'plan'];
export const SECTION_FIELDS: readonly SectionField[] = [...NOTE_FIELDS, 'tests', 'evolution', 'unassigned'];

export type WorkspaceSection = {
  id: string;
  field: SectionField;
  /** Heading exactly as the clinician wrote it (null when there was none). */
  heading: string | null;
  /** Exact original substring. Concatenating every `raw` reproduces the original. */
  raw: string;
  /** Body as detected; never changes after structuring. */
  proposed: string;
  /** Body the clinician may edit before building the final document. */
  body: string;
  include: boolean;
  applied: boolean;
};

const ALIASES: Record<Exclude<SectionField, 'unassigned'>, string[]> = {
  chief: ['motivo de consulta', 'motivo', 'mc', 'motivo da consulta', 'reason for visit', 'reason for consultation',
    'chief complaint', 'cc', 'queixa principal', 'queja principal', 'motivo de ingreso'],
  hpi: ['enfermedad actual', 'historia de la enfermedad actual', 'historia actual', 'anamnesis', 'hea', 'hpi',
    'history of present illness', 'historia da doenca atual', 'historia da doenca actual', 'doenca atual',
    'doenca actual', 'presenting complaint'],
  pmh: ['antecedentes', 'antecedentes personales', 'antecedentes medicos', 'antecedentes personales y familiares',
    'ap', 'past medical history', 'pmh', 'medical history', 'antecedentes pessoais', 'historia medica'],
  meds: ['tratamiento habitual', 'medicacion habitual', 'medicacion', 'medicacion domiciliaria', 'home medications',
    'medications', 'medicacao habitual', 'terapeutica habitual', 'medicacao'],
  allergies: ['alergias', 'alergias medicamentosas', 'allergies', 'alergias conocidas', 'alergias medicamentosas conocidas'],
  exam: ['exploracion', 'exploracion fisica', 'examen fisico', 'ef', 'exame objetivo', 'exame objectivo',
    'physical examination', 'physical exam', 'examination', 'exam', 'on examination', 'exame fisico'],
  tests: ['pruebas complementarias', 'pruebas', 'analitica', 'analitica y pruebas', 'resultados',
    'exploraciones complementarias', 'investigations', 'results', 'labs', 'laboratory', 'meios complementares',
    'exames complementares', 'mcdt', 'analises'],
  problems: ['juicio clinico', 'diagnostico', 'diagnosticos', 'impresion diagnostica', 'orientacion diagnostica',
    'problemas', 'lista de problemas', 'assessment', 'impression', 'diagnosis', 'problem list', 'avaliacao',
    'impressao diagnostica'],
  plan: ['plan', 'plan terapeutico', 'tratamiento', 'plan de tratamiento', 'treatment', 'treatment plan',
    'tratamento', 'plano', 'plano terapeutico', 'conducta'],
  evolution: ['evolucion', 'evolucion clinica', 'course', 'clinical course', 'hospital course', 'evolucao', 'progress'],
};

/** Case- and accent-insensitive comparison key. Used for matching only. */
function fold(text: string): string {
  return text.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/\s+/g, ' ').trim();
}

const LOOKUP = new Map<string, SectionField>(
  (Object.entries(ALIASES) as [SectionField, string[]][]).flatMap(([field, names]) => names.map(name => [fold(name), field] as const)),
);

type Heading = { field: SectionField; label: string; rest: string };

function detectHeading(line: string): Heading | null {
  const noEol = line.replace(/\r?\n$/, '');
  const stripped = noEol.replace(/^[\s#*_>\-•·\d.)(]*/u, '');
  const colon = stripped.search(/[:：]/);
  if (colon > 0 && colon <= 60) {
    const field = LOOKUP.get(fold(stripped.slice(0, colon).replace(/[*_\s]+$/u, '')));
    if (field) return { field, label: stripped.slice(0, colon + 1), rest: stripped.slice(colon + 1).replace(/^[*_\s]+/u, '') };
  }
  const whole = fold(stripped.replace(/[*_\s:：.\-–—]+$/u, ''));
  const field = whole ? LOOKUP.get(whole) : undefined;
  return field ? { field, label: stripped.trim(), rest: '' } : null;
}

/** Splits the clinician's text at the headings they wrote. Returns [] for blank input. */
export function structureText(original: string): WorkspaceSection[] {
  if (!original.trim()) return [];
  type Acc = { field: SectionField; heading: string | null; raw: string; parts: string[] };
  const done: Acc[] = [];
  let current: Acc | null = null;
  let carried = '';
  const flush = () => {
    if (!current) return;
    if (current.field === 'unassigned' && !current.raw.trim()) carried += current.raw;
    else { current.raw = carried + current.raw; carried = ''; done.push(current); }
    current = null;
  };
  for (const line of original.split(/(?<=\n)/)) {
    const heading = detectHeading(line);
    if (heading) {
      flush();
      const eol = /\r?\n$/.exec(line)?.[0] ?? '';
      current = { field: heading.field, heading: heading.label, raw: line, parts: [heading.rest + eol] };
    } else if (current) {
      current.raw += line;
      current.parts.push(line);
    } else {
      current = { field: 'unassigned', heading: null, raw: line, parts: [line] };
    }
  }
  flush();
  return done.map((section, index) => {
    const body = section.parts.join('').trim();
    return {
      id: `s${index}`, field: section.field, heading: section.heading, raw: section.raw,
      proposed: body, body, include: body.length > 0, applied: false,
    };
  });
}

export function isNoteField(field: SectionField): field is NoteField {
  return (NOTE_FIELDS as readonly string[]).includes(field);
}

/** Final document from the sections the clinician kept. Labels come from the interface language. */
export function assembleDocument(sections: WorkspaceSection[], labels: Record<SectionField, string>): string {
  return sections
    .filter(section => section.include && section.body.trim())
    .map(section => (section.field === 'unassigned' ? section.body.trim() : `${labels[section.field]}\n${section.body.trim()}`))
    .join('\n\n');
}

/** Adds text to a note field without ever overwriting or duplicating what is already there. */
export function appendToField(current: string, addition: string): { value: string; changed: boolean } {
  const text = addition.trim();
  if (!text) return { value: current, changed: false };
  // Only complete consecutive lines establish that this exact block is present.
  // A substring can reverse context ("asma" inside "sin asma") or change a number.
  const existing = current.split(/\r?\n/);
  const incoming = text.split(/\r?\n/);
  const alreadyPresent = existing.some((_, start) =>
    incoming.every((line, offset) => existing[start + offset] === line),
  );
  if (alreadyPresent) return { value: current, changed: false };
  return { value: current.trim() ? `${current.replace(/\s+$/, '')}\n${text}` : text, changed: true };
}

export type ApplicationPlan = {
  next: Record<NoteField, string>;
  appliedIds: string[];
  alreadyPresentIds: string[];
  noTargetIds: string[];
};

/** Pure preview of "apply to the note": which sections reach which field. Never overwrites. */
export function planApplication(sections: WorkspaceSection[], current: Record<NoteField, string>): ApplicationPlan {
  const plan: ApplicationPlan = { next: { ...current }, appliedIds: [], alreadyPresentIds: [], noTargetIds: [] };
  for (const section of sections) {
    if (!section.include || !section.body.trim()) continue;
    if (!isNoteField(section.field)) { plan.noTargetIds.push(section.id); continue; }
    const result = appendToField(plan.next[section.field], section.body);
    plan.next[section.field] = result.value;
    (result.changed ? plan.appliedIds : plan.alreadyPresentIds).push(section.id);
  }
  return plan;
}
