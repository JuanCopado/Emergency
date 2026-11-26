import type { ClinicalNotePayload, TherapeuticPlan, TherapeuticReview, TherapyContext, TherapySelection } from '../../clinical-note/types';

export const SYNTHETIC_THERAPY_SELECTION: TherapySelection = { label: 'SYNTHETIC_DIAGNOSIS', module_id: 'synthetic-module', selection: 'manual' };
export function syntheticTherapeuticPlan(note: ClinicalNotePayload, selection: TherapySelection, context: TherapyContext): TherapeuticPlan {
  return {
    schema_version: '1.0', plan_id: 'synthetic-plan', diagnosis: selection,
    population: note.encounter.age.months !== null || (note.encounter.age.years !== null && note.encounter.age.years < 18) ? 'pediatric' : 'adult',
    context, sections: {
      initial_actions: 'SYNTHETIC_INITIAL_ACTIONS', medications: 'SYNTHETIC_MEDICATION_REGIMEN',
      monitoring: 'SYNTHETIC_MONITORING', reassessment: 'SYNTHETIC_REASSESSMENT', disposition: 'SYNTHETIC_DISPOSITION',
    },
    source_refs: [{ module_id: 'synthetic-module', path: 'clinical/modules/synthetic.md', sha256: 'a'.repeat(64), language: 'original' }],
    reference_text: 'SYNTHETIC_CANONICAL_REFERENCE_UNCHANGED', source_revision: 'b'.repeat(40),
    generated_from_digest: 'c'.repeat(64), generation_token: 'synthetic-generation-token',
    suggested_content_digest: 'd'.repeat(64), missing_requirements: [],
    medication_safety: { status: 'REVIEW_REQUIRED', actionable: false, required_module: 'medication-selection-safety' },
  };
}
export function syntheticTherapeuticReview(mode: 'as_suggested'|'edited' = 'as_suggested'): TherapeuticReview {
  return {
    status: 'validated', mode, scope: 'physician_review_of_this_version',
    confirmations: { individualized: true, medication_safety_reviewed: true },
    reviewed_at: '2026-11-26T12:00:00Z', plan_digest: 'e'.repeat(64), context_digest: 'f'.repeat(64), validation_token: 'synthetic-validation-token',
  };
}
