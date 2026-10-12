"""Ensure CI executes the independently sourced v1.44 synthetic expectations."""
import sys
import unittest
import json
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'qa'))
from run_functional_v144 import QA, run, build, analyze, export_note_bytes
from clinical_note_support import new_note


class FunctionalV144Tests(unittest.TestCase):
    def test_bank_preserves_expectations_gates_api_and_exports(self):
        report = run()
        self.assertEqual(len(report['cases']), 20)
        for case in report['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(case['status'], 'PASS', case)

    def test_duplicate_ecg_does_not_amplify_assessment(self):
        case = json.loads((QA / 'V1.44_DEMO_CASES.json').read_text(encoding='utf-8'))['cases'][0]['input']
        note = build(case)
        first = analyze(deepcopy(note), apply_to_note=True)
        note['complementary_tests']['ecg'] *= 2
        second = analyze(note, apply_to_note=True)
        self.assertEqual(first['assessment'], second['assessment'])

    def test_empty_note_does_not_invent_likely_diagnosis(self):
        result = analyze(new_note(age_years=50), apply_to_note=True)
        self.assertEqual(result['assessment']['likely_diagnoses'], [])
        self.assertTrue(result['assessment']['limitations'])

    def test_invalid_export_format_fails_after_review(self):
        case = json.loads((QA / 'V1.44_DEMO_CASES.json').read_text(encoding='utf-8'))['cases'][0]['input']
        note = analyze(build(case), apply_to_note=True)['note']
        note['clinician_validation'].update(reviewed=True, reviewer_role='treating_clinician')
        for fmt in ('', 'exe', None, {}, []):
            with self.subTest(format=fmt), self.assertRaisesRegex(ValueError, 'format must be'):
                export_note_bytes(note, fmt)


if __name__ == '__main__':
    unittest.main()
