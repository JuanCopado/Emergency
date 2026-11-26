"""Exercise the real review API with non-prescribing, synthetic QA content only.

Never imported by the application. These confirmations simulate a test operator;
they are neither a medical review nor a migration of an actual historical note.
"""
from clinical_note_api import dispatch


def review_synthetic_plan(note):
    status, draft = dispatch('/api/clinical-note/therapy/suggest', {
        'note': note,
        'selection': {'label': 'Synthetic QA workflow', 'module_id': None, 'selection': 'manual'},
        'context': {'weight_kg': None, 'allergies_reviewed': True},
    })
    assert status == 200 and not draft['blocked'], draft
    note['therapeutic_plan'] = draft['plan']
    note.pop('therapeutic_review', None)
    note['therapeutic_plan']['sections'] = {
        'initial_actions': 'Synthetic QA initial actions; no real clinical intervention.',
        'medications': 'Synthetic QA only; no medication prescribed.',
        'monitoring': 'Synthetic QA monitoring; no real patient.',
        'reassessment': 'Synthetic QA reassessment; no real patient.',
        'disposition': 'Synthetic QA follow-up; no real patient.',
    }
    status, reviewed = dispatch('/api/clinical-note/therapy/validate', {
        'note': note,
        'confirmations': {'individualized': True, 'medication_safety_reviewed': True},
    })
    assert status == 200 and not reviewed['blocked'], reviewed
    note['therapeutic_review'] = reviewed['review']
    return note
