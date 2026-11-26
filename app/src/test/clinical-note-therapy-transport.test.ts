// Integration of PR114 transport failures with PR116's typed review refusals.
import { afterEach, expect, it, vi } from 'vitest';
import { ClinicalApiResponseError, exportClinicalNote, suggestTherapeuticPlan, validateTherapeuticPlan } from '../clinical-note/api';
import type { ClinicalNotePayload } from '../clinical-note/types';

const note = {} as ClinicalNotePayload;
const operations = [
  ['suggest', () => suggestTherapeuticPlan(note, { label: 'Synthetic QA', module_id: null, selection: 'manual' }, { weight_kg: null, allergies_reviewed: true })],
  ['validate', () => validateTherapeuticPlan(note, { individualized: true, medication_safety_reviewed: true })],
  ['export', () => exportClinicalNote(note, 'json')],
] as const;
afterEach(() => vi.unstubAllGlobals());

it.each(operations)('%s rejects malformed HTTP 200 bodies without exposing their content', async (_name, operation) => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response('SYNTHETIC_PRIVATE_BODY', { status: 200 })));
  await expect(operation()).rejects.toThrow(/^Invalid backend response$/);
});

it.each(operations)('%s preserves authoritative review error status and code', async (_name, operation) => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ error: 'Synthetic stale review', error_code: 'THERAPY_REVIEW_INVALID' }), { status: 409 })));
  const failure = await operation().catch(error => error);
  expect(failure).toBeInstanceOf(ClinicalApiResponseError);
  expect(failure.status).toBe(409);
  expect(failure.code).toBe('THERAPY_REVIEW_INVALID');
  expect(failure.message).toBe('Synthetic stale review');
});
