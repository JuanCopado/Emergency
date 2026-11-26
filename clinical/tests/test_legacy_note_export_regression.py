"""Legacy non-therapeutic exports and version-bound treatment review coexist."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'qa'))
from run_functional_v144 import QA, analyze, build, export_note_bytes
from clinical_note_exporter import export_docx, export_json, export_pdf
from clinical_note_support import new_note, validate_for_export
from synthetic_therapy_review import review_synthetic_plan
from tempfile import TemporaryDirectory


class LegacyNoteExportRegressionTests(unittest.TestCase):
    def legacy_note(self):
        note = new_note(age_years=45)
        note['privacy'].update(direct_identifiers_removed=True, free_text_screened=True,
                               source_metadata_checked=True, burned_in_identifiers_checked=True)
        note['clinician_validation'].update(reviewed=True, reviewer_role='treating_clinician')
        return note

    def test_historical_note_without_therapy_remains_exportable_in_all_formats(self):
        note = self.legacy_note()
        self.assertFalse(validate_for_export(note)['blocked'])
        self.assertEqual(json.loads(export_note_bytes(note, 'json')), note)
        for fmt, magic in (('pdf', b'%PDF'), ('docx', b'PK')):
            with self.subTest(format=fmt):
                self.assertTrue(export_note_bytes(note, fmt).startswith(magic))

    def test_all_historical_therapeutic_cases_require_real_review(self):
        bank = json.loads((QA / 'V1.44_DEMO_CASES.json').read_text())
        for case in bank['cases']:
            if case['layer'] != 'note':
                continue
            with self.subTest(case=case['id']):
                note = analyze(build(case['input']), apply_to_note=True)['note']
                assessment = deepcopy(note['assessment'])
                note['clinician_validation']['reviewed'] = True
                self.assertTrue(validate_for_export(note)['blocked'])
                review_synthetic_plan(note)
                self.assertFalse(validate_for_export(note)['blocked'])
                exported = json.loads(export_note_bytes(note, 'json'))
                self.assertEqual(note['assessment'], assessment)
                for key, value in assessment.items():
                    self.assertEqual(exported['assessment'][key], [] if key in
                                     ('treatment_suggestions', 'disposition', 'reassessment') else value)
                self.assertEqual(exported['therapeutic_plan'], note['therapeutic_plan'])

    def test_privacy_and_clinician_gates_still_block_historical_notes(self):
        for section, key in (('privacy', 'direct_identifiers_removed'),
                             ('privacy', 'free_text_screened'),
                             ('privacy', 'source_metadata_checked'),
                             ('clinician_validation', 'reviewed')):
            note = self.legacy_note()
            if key == 'source_metadata_checked':
                note['privacy']['mode'] = 'external_anonymized'
            note[section][key] = False
            with self.subTest(gate=key):
                self.assertTrue(validate_for_export(note)['blocked'])

    def test_missing_forged_and_stale_plan_block_all_export_entry_points(self):
        signed = review_synthetic_plan(self.legacy_note())
        for mutation in ('missing', 'forged', 'stale', 'edited'):
            note = deepcopy(signed)
            if mutation == 'missing':
                del note['therapeutic_plan']
            elif mutation == 'forged':
                note['therapeutic_review']['validation_token'] = '0' * 64
            elif mutation == 'stale':
                note['history']['present_illness'] = 'Synthetic changed context'
            else:
                note['therapeutic_plan']['sections']['medications'] += ' Edited.'
            for fmt in ('json', 'pdf', 'docx'):
                with self.subTest(mutation=mutation, format=fmt), self.assertRaises(ValueError):
                    export_note_bytes(note, fmt)
            with TemporaryDirectory() as directory:
                for exporter in (export_json, export_pdf, export_docx):
                    with self.subTest(mutation=mutation, entry=exporter.__name__), self.assertRaises(ValueError):
                        exporter(note, Path(directory) / 'blocked')

