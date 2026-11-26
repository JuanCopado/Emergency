import type { ClinicalNotePayload, TherapeuticPlan, TherapeuticReview, TherapeuticSections, TherapyContext, TherapySelection } from './types';

export const THERAPEUTIC_SECTION_KEYS = ['initial_actions', 'medications', 'monitoring', 'reassessment', 'disposition'] as const satisfies readonly (keyof TherapeuticSections)[];

/** A local exact comparison only. The backend independently verifies its signed receipt. */
function stable(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stable).join(',')}]`;
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).filter(key => record[key] !== undefined).sort().map(key => `${JSON.stringify(key)}:${stable(record[key])}`).join(',')}}`;
  }
  return JSON.stringify(value) ?? 'null';
}

function clinicalContext(note: ClinicalNotePayload) {
  // These are outputs or attestations, not inputs to the exact clinical version.
  // The server binds the same case fields; this string is never an authorization token.
  const { therapeutic_plan: _plan, therapeutic_review: _review, clinician_validation: _validation, ...rest } = note;
  const { export_allowed: _allowed, ...privacy } = rest.privacy;
  const { treatment_suggestions: _suggestions, disposition: _disposition, reassessment: _reassessment, ...assessment } = rest.assessment;
  void _plan; void _review; void _validation; void _allowed; void _suggestions; void _disposition; void _reassessment;
  return { ...rest, privacy, assessment };
}

export function therapyContextSnapshot(note: ClinicalNotePayload, selection: TherapySelection, context: TherapyContext): string {
  return stable({ note: clinicalContext(note), selection, context });
}

export function therapyReviewSnapshot(note: ClinicalNotePayload): string {
  return stable({ note: clinicalContext(note), plan: note.therapeutic_plan ?? null });
}

export function therapySourceSnapshot(plan: TherapeuticPlan): string {
  return stable({ plan_id: plan.plan_id, generation_token: plan.generation_token, source_revision: plan.source_revision, source_refs: plan.source_refs, reference_text: plan.reference_text });
}

export function hasTherapeuticReceipt(review: TherapeuticReview | null): review is TherapeuticReview {
  return Boolean(review?.status === 'validated' && review.scope === 'physician_review_of_this_version' &&
    review.confirmations?.individualized && review.confirmations.medication_safety_reviewed &&
    review.validation_token && review.plan_digest && review.context_digest && review.reviewed_at);
}
