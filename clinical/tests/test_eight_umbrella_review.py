"""Prevent dangerous delays and implicit approval of unreviewed child pathways."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load


class UmbrellaSafetyTests(unittest.TestCase):
    def check_boundaries(self, module, boundaries):
        text = ' '.join(load(ROOT, module).split())
        for boundary in boundaries:
            with self.subTest(module=module, boundary=boundary):
                self.assertIn(boundary, text)

    def test_endocrine_does_not_delay_rescue_or_mix_insulin_indications(self):
        self.check_boundaries('endocrine-metabolic', [
            'do not delay treatment of suspected adrenal crisis or severe hypoglycemia',
            'Do not interchange DKA, isolated HHS and routine ICU hyperglycemia regimens',
            'only when the patient is alert enough to swallow safely',
            'sampling/imaging must not delay it',
            'not automatic for every suspected apoplexy',
        ])

    def test_ent_prioritizes_airway_and_preserves_anticoagulant_context(self):
        self.check_boundaries('ent-emergencies', [
            'A normal visible oropharynx does not exclude supraglottitis',
            'before a threatened airway is secured',
            'do not automatically stop/reverse anticoagulation before local first-line treatment',
            'within the past 30 days requires review within 24 hours',
            'not repeated blind attempts',
        ])

    def test_environmental_rescue_is_specific_to_temperature_and_hypoxia(self):
        self.check_boundaries('environmental-emergencies', [
            'do not postpone cooling', 'Antipyretics do not treat heat stroke',
            'temperature-modified resuscitation protocol',
            '5 rescue breaths then standard CPR when indicated',
            'must not delay essential extrication/resuscitation',
            'not every specialist exposure-treatment regimen',
        ])

    def test_geriatrics_does_not_equate_frailty_with_futility_or_bacteriuria_with_uti(self):
        self.check_boundaries('geriatric-emergencies', [
            'chronological age or a frailty score alone must not determine treatment limitation',
            'Do not diagnose or treat UTI from delirium/fall plus bacteriuria alone',
            'does not apply to an unstable patient with suspected sepsis',
            'caregiver capacity makes discharge unsafe',
        ])

    def test_oncology_does_not_delay_sepsis_or_ignore_tls_contraindications(self):
        self.check_boundaries('hematology-oncology', [
            'without waiting for the neutrophil count or culture results',
            'Prevention and established TLS require different specialist regimens',
            'rasburicase is contraindicated in G6PD deficiency',
            'Do not routinely correct asymptomatic TLS-associated hypocalcemia',
            'A cell count alone cannot determine leukostasis',
        ])

    def test_electrolyte_framework_does_not_enable_unresolved_preparations(self):
        self.check_boundaries('electrolytes', [
            'confirm unexpected results without delaying life-saving therapy',
            'normal ECG excludes dangerous hyperkalemia',
            'do not use a generic replacement plan',
            'Never give concentrated potassium as an IV push',
            'does not approve an unresolved sodium preparation',
        ])
        # This phrase must be inside the explicit negation, not a reassurance.
        self.assertIn('do not assume every high result is artifactual or that a normal ECG excludes',
                      ' '.join(load(ROOT, 'electrolytes').split()))

    def test_infectious_framework_does_not_wait_for_tests_or_current_antibiogram(self):
        self.check_boundaries('emergency-infectious-diseases', [
            'at triage, without waiting for confirmatory testing',
            'if this causes no clinically important delay',
            'local resistance data can change the initial empirical choice',
            'do not invent one notification deadline',
            'not validation of every pathogen-specific regimen',
        ])

    def test_procedure_framework_does_not_promote_individual_techniques(self):
        self.check_boundaries('emergency-procedures', [
            '196 procedimientos canónicos y 4 alias',
            'Una lista completada no acredita competencia técnica',
            'cuándo detenerse, cambiar de estrategia o pedir ayuda',
            'confirmación apropiada de posición o función',
            'No promueve las 196 fichas individuales',
            'no habilita contratos farmacológicos bloqueados',
        ])


if __name__ == '__main__':
    unittest.main()
