import { describe, expect, it } from 'vitest';
import { appendToField, assembleDocument, planApplication, structureText, SECTION_FIELDS, type NoteField, type SectionField } from './textStructuring';

const labels = Object.fromEntries(SECTION_FIELDS.map(field => [field, field.toUpperCase()])) as Record<SectionField, string>;
const empty = (): Record<NoteField, string> => ({ chief: '', hpi: '', pmh: '', meds: '', allergies: '', exam: '', problems: '', plan: '' });
const joinRaw = (text: string) => structureText(text).map(section => section.raw).join('');
const ecmaWhitespace = [
  0x0009, 0x000a, 0x000b, 0x000c, 0x000d, 0x0020, 0x00a0, 0x1680,
  0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007,
  0x2008, 0x2009, 0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000, 0xfeff,
].map(code => String.fromCodePoint(code));

const SYNTHETIC_ES = `Paciente sintético sin datos reales.
Motivo de consulta: disnea de 2 días
ANTECEDENTES
HTA, DM2
Alergias: ninguna conocida
Exploración física: TA 120/80, FC 90
Pruebas complementarias:
Hb 12 g/dL
Plan: observación y reevaluación`;

describe('structureText', () => {
  it('preserves Unicode whitespace behaviour when trimming heading punctuation', () => {
    // CR/LF delimit input lines; the other ECMAScript whitespace characters can
    // occur inside a heading suffix, including NBSP, em space and BOM.
    for (const whitespace of ecmaWhitespace.filter(character => character !== '\r' && character !== '\n')) {
      for (const heading of [`Plan${whitespace}*_`, `Plan*${whitespace}_:`]) {
        const text = `${heading}\nobservación sintética`;
        const sections = structureText(text);
        expect(sections).toHaveLength(1);
        expect(sections[0]).toMatchObject({ field: 'plan', body: 'observación sintética' });
        expect(joinRaw(text)).toBe(text);
      }
    }
    expect(structureText('Plan\u200b*_\ntexto sintético')[0]!.field).toBe('unassigned');
  });

  it('splits at the headings the clinician wrote and keeps their wording verbatim', () => {
    const sections = structureText(SYNTHETIC_ES);
    expect(sections.map(section => section.field)).toEqual(['unassigned', 'chief', 'pmh', 'allergies', 'exam', 'tests', 'plan']);
    expect(sections[1]).toMatchObject({ heading: 'Motivo de consulta:', body: 'disnea de 2 días' });
    expect(sections[2]!.body).toBe('HTA, DM2');
    expect(sections[5]!.body).toBe('Hb 12 g/dL');
    expect(sections[0]!.heading).toBeNull();
  });

  it('is lossless: every character of the original lands in exactly one section', () => {
    for (const text of [
      SYNTHETIC_ES,
      SYNTHETIC_ES.replace(/\n/g, '\r\n'),
      `\n\n  Plan: x\n\n\nAlergias:\n  penicilina\n`,
      'sin encabezados\nsolo texto libre\n',
      'Plan\nPlan: segundo\nPlan:',
      '# Exploración\n**Plan:** reposo\n1. Antecedentes: asma',
    ]) expect(joinRaw(text)).toBe(text);
  });

  it('keeps the unassigned lead text and never invents a section', () => {
    const sections = structureText('texto sin cabeceras\notra línea');
    expect(sections).toHaveLength(1);
    expect(sections[0]).toMatchObject({ field: 'unassigned', heading: null, body: 'texto sin cabeceras\notra línea' });
    expect(structureText('')).toEqual([]);
    expect(structureText('  \n \n')).toEqual([]);
  });

  it('recognises Portuguese and English headings, ignoring case and accents', () => {
    const pt = structureText('Antecedentes pessoais: asma\nExame objetivo: sem alterações\nPlano: alta');
    expect(pt.map(section => section.field)).toEqual(['pmh', 'exam', 'plan']);
    const en = structureText('chief complaint: chest pain\nPast Medical History: none\nTreatment: observe');
    expect(en.map(section => section.field)).toEqual(['chief', 'pmh', 'plan']);
    expect(structureText('EXPLORACION FISICA: normal')[0]!.field).toBe('exam');
  });

  it('does not treat narrative text that merely mentions a heading word as a heading', () => {
    const sections = structureText('El plan de la familia era viajar, sin tratamiento previo.\nAntecedentes: HTA');
    expect(sections.map(section => section.field)).toEqual(['unassigned', 'pmh']);
    expect(sections[0]!.body).toContain('El plan de la familia');
  });

  it('does not include empty sections by default and keeps proposed separate from editable body', () => {
    const [empty, filled] = structureText('Plan:\nAlergias: ninguna');
    expect(empty).toMatchObject({ field: 'plan', body: '', include: false });
    expect(filled).toMatchObject({ field: 'allergies', proposed: 'ninguna', body: 'ninguna', include: true });
  });
});

describe('assembleDocument', () => {
  it('uses the chosen field label, omits excluded sections and keeps the body untouched', () => {
    const sections = structureText(SYNTHETIC_ES);
    sections[3]!.include = false;
    const document = assembleDocument(sections, labels);
    expect(document).toContain('CHIEF\ndisnea de 2 días');
    expect(document).toContain('Paciente sintético sin datos reales.');
    expect(document).not.toContain('ALLERGIES');
    expect(document).not.toContain('Alergias');
  });
});

describe('appendToField / planApplication', () => {
  it('trims every ECMAScript trailing whitespace character without dropping non-whitespace', () => {
    for (const whitespace of ecmaWhitespace) {
      expect(appendToField(`texto sintético${whitespace}`, 'sección nueva')).toEqual({
        value: 'texto sintético\nsección nueva', changed: true,
      });
    }
    expect(appendToField('texto sintético\u200b', 'sección nueva').value).toBe('texto sintético\u200b\nsección nueva');
  });

  it.each([
    ['Sin asma', 'asma'],
    ['Sin alergia a penicilina', 'alergia a penicilina'],
    ['Observación 24 horas', '4 horas'],
    ['prefijo HTA sufijo', 'HTA'],
  ])('does not suppress a substring in a different context: %s / %s', (current, addition) => {
    expect(appendToField(current, addition)).toEqual({ value: `${current}\n${addition}`, changed: true });
  });

  it('recognises only complete consecutive multiline blocks, including CRLF', () => {
    expect(appendToField('Antes\nprimera\nsegunda\nDespués', 'primera\nsegunda')).toEqual({
      value: 'Antes\nprimera\nsegunda\nDespués', changed: false,
    });
    expect(appendToField('Antes\r\nprimera\r\nsegunda\r\nDespués', 'primera\nsegunda')).toEqual({
      value: 'Antes\r\nprimera\r\nsegunda\r\nDespués', changed: false,
    });
    expect(appendToField('primera\nintermedio\nsegunda', 'primera\nsegunda').changed).toBe(true);
    expect(appendToField('prefijo primera\nsegunda sufijo', 'primera\nsegunda').changed).toBe(true);
  });

  it('preserves a new affirmative section after a negation and remains idempotent on reapplication', () => {
    const sections = structureText('Alergias: alergia a penicilina');
    const current = { ...empty(), allergies: 'Sin alergia a penicilina' };
    const first = planApplication(sections, current);
    expect(first.next.allergies).toBe('Sin alergia a penicilina\nalergia a penicilina');
    expect(first.appliedIds).toEqual(['s0']);
    expect(first.alreadyPresentIds).toEqual([]);
    const second = planApplication(sections, first.next);
    expect(second.next).toEqual(first.next);
    expect(second.appliedIds).toEqual([]);
    expect(second.alreadyPresentIds).toEqual(['s0']);
  });

  it('appends without overwriting and never duplicates', () => {
    expect(appendToField('', ' HTA ')).toEqual({ value: 'HTA', changed: true });
    expect(appendToField('DM2\n', 'HTA')).toEqual({ value: 'DM2\nHTA', changed: true });
    expect(appendToField('DM2\nHTA', 'HTA')).toEqual({ value: 'DM2\nHTA', changed: false });
    expect(appendToField('x', '   ')).toEqual({ value: 'x', changed: false });
  });

  it('reports applied, already present and no-target sections, and keeps existing field content', () => {
    const sections = structureText(SYNTHETIC_ES);
    const current = { ...empty(), pmh: 'Asma previa', allergies: 'ninguna conocida' };
    const plan = planApplication(sections, current);
    expect(plan.next.pmh).toBe('Asma previa\nHTA, DM2');
    expect(plan.next.chief).toBe('disnea de 2 días');
    expect(plan.next.allergies).toBe('ninguna conocida');
    expect(plan.alreadyPresentIds).toEqual(['s3']);
    expect(plan.noTargetIds).toEqual(['s0', 's5']);
    expect(current.pmh).toBe('Asma previa');
  });
});
