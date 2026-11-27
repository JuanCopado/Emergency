import { expect, it } from 'vitest';
import { therapyContextSnapshot } from '../clinical-note/therapeuticReview';
import type { ClinicalNotePayload, TherapyContext, TherapySelection } from '../clinical-note/types';

// Synthetic structural inputs; no prescription or clinical inference.
const note = {
  history: { chief_complaint: 'Synthetic complaint', present_illness: 'é / 中 / β' },
  privacy: { mode: 'clinical_pseudonymized', export_allowed: false },
  assessment: { treatment_suggestions: [], disposition: [], reassessment: [], active_problems: ['Synthetic problem'] },
} as unknown as ClinicalNotePayload;
const selection: TherapySelection = { label: 'Synthetic selection', module_id: null, selection: 'manual' };
const context: TherapyContext = { weight_kg: null, allergies_reviewed: true };
const snapshot = (value: ClinicalNotePayload) => therapyContextSnapshot(value, selection, context);

it('object insertion order cannot invalidate an unchanged clinical version', () => {
  const reordered = { ...note, history: Object.fromEntries(Object.entries(note.history).reverse()) as typeof note.history };
  expect(snapshot(reordered)).toBe(snapshot(note));
});

it('changed Unicode clinical text is a different version', () => {
  const changed = { ...note, history: { ...note.history, present_illness: 'e / 中 / β' } };
  expect(snapshot(changed)).not.toBe(snapshot(note));
});

it('a changed medication safety context is a different version', () => {
  expect(therapyContextSnapshot(note, selection, { ...context, allergies_reviewed: false })).not.toBe(snapshot(note));
});
