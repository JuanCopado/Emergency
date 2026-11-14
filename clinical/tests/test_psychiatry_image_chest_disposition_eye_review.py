"""Regressions for critical safety limits in five reviewed adult frameworks."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load


class FiveFrameworkSafetyTests(unittest.TestCase):
    def check_boundaries(self, module, boundaries):
        text = ' '.join(load(ROOT, module).split())
        for boundary in boundaries:
            with self.subTest(module=module, boundary=boundary):
                self.assertIn(boundary, text)

    def test_psychiatric_evaluation_does_not_shortcut_physical_or_capacity_assessment(self):
        self.check_boundaries('psychiatric-emergencies', [
            'a psychiatric history does not exclude physical illness',
            'does not justify withholding tests in delirium, poisoning, instability',
            'Do not use coercion as punishment or convenience',
            'Do not copy procedural-sedation doses',
            'diagnosis or a family request alone does not establish compulsory treatment',
            'improvement in agitation alone is not medical clearance',
        ])

    def test_im_olanzapine_warning_is_direction_specific_and_not_all_antipsychotics(self):
        self.check_boundaries('psychiatric-emergencies', [
            'simultaneous IM olanzapine and parenteral benzodiazepine is not recommended',
            'wait at least 1 hour',
            'rather than assuming a symmetric automatic interval',
            'particularly during the first 4 hours after IM olanzapine',
            'not a general waiting rule for every antipsychotic',
        ])

    def test_radiography_preserves_occult_fracture_and_unvalidated_accuracy_boundaries(self):
        self.check_boundaries('musculoskeletal-xray', [
            'A negative radiograph does not exclude an occult fracture',
            'MRI is unavailable within 24 hours or contraindicated',
            'do not apply an adult classification',
            'does not establish diagnostic accuracy',
            'No new patient images or independently adjudicated image cases were assessed',
        ])
        reg = json.loads((ROOT / 'references/evidence-registry.json').read_text())
        self.assertEqual(reg['modules']['clinical-image-interpretation']['status'], 'yellow')

    def test_chest_pain_does_not_reassure_from_labels_or_one_negative_test(self):
        self.check_boundaries('non-coronary-chest-pain', [
            "'non-coronary' is not an initial rule-out diagnosis",
            'A single normal ECG does not exclude ACS',
            'do not invent one threshold or interval for every assay',
            'a normal chest X-ray or limited POCUS cannot exclude PE, dissection',
            'no risk score alone establishes safety',
        ])

    def test_discharge_requires_safe_endpoints_and_closed_loop_result_ownership(self):
        self.check_boundaries('observation-discharge', [
            'not a place to defer necessary admission or source control',
            'do not impose one observation time for all conditions',
            'name the clinician/service responsible for reviewing it',
            "'no news means normal' is not closed-loop follow-up",
            'must not be left unresolved merely because follow-up is planned',
        ])

    def test_eye_emergencies_preserve_irrigation_open_globe_and_mechanism_specific_care(self):
        self.check_boundaries('ophthalmology-emergencies', [
            'begin copious irrigation immediately',
            'no fixed volume alone proves adequate decontamination',
            'avoid manipulation, tonometry and pressure-producing ocular ultrasound',
            'do not remove an embedded object',
            'not an automatic ocular massage, paracentesis or empiric thrombolysis order',
            'do not give a universal pilocarpine regimen',
            'do not treat these as uncomplicated conjunctivitis',
        ])


if __name__ == '__main__':
    unittest.main()
