import { expect, it } from 'vitest';
import generated from '../data/generatedProcedures.json';
import { getCanonicalGuide } from '../clinical-guides/canonical';
import { getRelatedProcedures } from '../clinical-guides/relatedProcedures';
import { getCanonicalProcedure } from '../clinical-guides/procedures';

it('contains 196 unique canonical procedures spanning all 16 families', () => {
  expect(generated).toHaveLength(196);
  expect(new Set(generated.map((p) => p.id)).size).toBe(196);
  expect(new Set(generated.map((p) => p.family)).size).toBe(16);
});

it('includes clinical procedures both excluded and included in the visual filter', () => {
  expect(generated.some((p) => p.id === 'PROC-VASC-001')).toBe(true);
  expect(generated.some((p) => p.id === 'PROC-VASC-007')).toBe(true);
});

it('related procedure recommendations use the complete clinical catalog', () => {
  const guide = getCanonicalGuide('undifferentiated-shock');
  if (!guide) throw new Error('Missing shock module');
  const related = getRelatedProcedures(guide, 200);
  expect(related.some((p) => p.id === 'PROC-VASC-001')).toBe(true);
  expect(related.some((p) => p.id === 'PROC-VASC-007')).toBe(true);
  expect(new Set(related.map((p) => p.id)).size).toBe(related.length);
});

it.each([
  ['PROC-ENT-011', 'PROC-ORTHO-022'],
  ['PROC-PED-008', 'PROC-ORTHO-004'],
  ['PROC-SP-006', 'PROC-EYE-001'],
  ['PROC-US-007', 'PROC-CV-006'],
])('resolves %s to its canonical procedure and source %s', (alias, target) => {
  const procedure = getCanonicalProcedure(alias);
  expect(procedure).toBe(getCanonicalProcedure(target));
  expect(procedure?.id).toBe(target);
  expect(procedure?.sourcePath).toMatch(/^clinical\/modules\/procedures\//);
  expect(procedure?.sourceHeading).toContain(target);
  expect(procedure?.aliases).toContain(alias);
  expect(generated.some((p) => p.id === alias)).toBe(false);
});

it('does not invent a canonical destination for an unknown procedure', () => {
  expect(getCanonicalProcedure('PROC-NOT-999')).toBeUndefined();
});
