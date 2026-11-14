"""Critical source boundaries and arithmetic for ten reviewed emergency references."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load
from pediatric_emergency_calculator import weight_based_total, volume_for_dose
from pediatric_bolus_calculator import calculate as bolus


class TenEmergencyReviewTests(unittest.TestCase):
    def boundaries(self, module, phrases):
        text = ' '.join(load(ROOT, module).split())
        for phrase in phrases:
            with self.subTest(module=module, phrase=phrase):
                self.assertIn(phrase, text)
        return text

    def test_syncope_requires_risk_context_and_safe_disposition(self):
        self.boundaries('syncope-falls-frailty', [
            'brief jerking can occur in syncope',
            'a postural drop does not automatically exclude',
            'Do not discharge based on a risk score alone',
            'do not invent a universal restriction interval',
        ])

    def test_young_infant_does_not_send_low_risk_neonates_home_or_delay_treatment_for_lp(self):
        self.boundaries('febrile-infant-0-90-days', [
            'Selected CPS 2026 pathway, 0–28 days',
            'Hospital observation is required even when',
            'do not delay empiric antibiotics/acyclovir for an unsafe or delayed LP',
            'Do not substitute the AAP8–21/22–28-day branches',
            'A positive viral test does not cancel',
        ])

    def test_bronchiolitis_records_discharge_and_portugal_difference(self):
        self.boundaries('bronchiolitis', [
            '4 hours including sleep',
            'over 90% at age ≥6 weeks',
            'over 92% if <6 weeks',
            'DGS Norma 016/2012',
            'does not claim DGS-equivalent thresholds',
            'specialist ICU exception, not a routine ward/ED prescription',
        ])

    def test_croup_keeps_severity_dose_and_exact_nebulized_concentration(self):
        self.boundaries('croup', [
            'Selected RCH severity-based approach', '**0.15 mg/kg**',
            '0.6 mg/kg (maximum 12 mg per current RCH guidance)',
            'L-epinephrine 1 mg/mL, 5 mL nebulized',
            'Racemic and L-epinephrine concentrations/volumes are not interchangeable',
            'after the **last** nebulized epinephrine dose',
        ])

    def test_pediatric_fluid_bolus_does_not_erase_neonatal_or_sepsis_scope(self):
        self.boundaries('pediatric-dehydration-shock', [
            'maximum 250 mL', 'under 16 non-neonatal sepsis context',
            '10–20 mL/kg', 'not a maximum for every indication',
            'do not wait to reach a fixed cumulative fluid total',
        ])

    def test_status_retains_hse_sequence_and_product_gate(self):
        self.boundaries('pediatric-status-epilepticus', [
            'no more than **2 total doses**', '40 mg/kg (max 3 g)',
            '50 mg/mL', 'do not combine its boluses/maxima with the HSE sequence',
            'not universal product-label compatibility',
            'not a reason to ignore ongoing convulsive status',
        ])

    def test_adult_arrhythmia_does_not_delay_shock_or_invent_pump_rate(self):
        self.boundaries('adult-arrhythmias', [
            '70--120 J', '120--150 J',
            'sedation and IV preparation must not delay rescue',
            'do not invent mL/h from a drug name',
        ])

    def test_adult_stacked_shocks_have_a_distinct_algorithm_counter(self):
        self.boundaries('adult-cardiac-arrest', [
            'count as **one algorithm shock**',
            'Do not give the routine third-shock drugs merely because three rapid',
            'does not encode this exceptional shock counter',
            'not the same as the pediatric monitored exception',
        ])

    def test_pediatric_bradycardia_does_not_use_small_dose_after_cpr_indicated(self):
        self.boundaries('pediatric-arrhythmias', [
            'Once CPR is indicated', '10 micrograms/kg IV/IO (max 1 mg)',
            'not the small pre-arrest dose',
            'For pre-arrest bradycardia that has not met the CPR criterion',
            'February 2026 Version 6',
        ])

    def test_pediatric_stacked_exception_is_corrected_against_erc_text(self):
        text = self.boundaries('pediatric-cardiac-arrest', [
            'amiodarone after the third stacked shock',
            'adrenaline after 4 minutes',
            'second amiodarone **after the fifth shock**',
            'Do not move the pediatric doses to a fifth/seventh-shock scheme',
            'more than 5 shocks',
        ])
        self.assertNotIn('a second amiodarone after the 7th shock', text)

    def test_severe_croup_existing_calculator_matches_selected_reference_cap(self):
        self.assertEqual(bolus('croup-dexamethasone-severe', 10)['dose'], 6)
        self.assertEqual(bolus('croup-dexamethasone-severe', 30)['dose'], 12)

    def test_reference_dose_caps_and_unit_conversion_on_synthetic_weights(self):
        # Arithmetic-only checks; no patient prescription, compatibility or stock claim.
        self.assertEqual(weight_based_total(40, 20, 3000)['total_dose'], 800)
        self.assertEqual(volume_for_dose(800, 50), 16)
        self.assertEqual(weight_based_total(40, 100, 3000)['total_dose'], 3000)
        self.assertEqual(weight_based_total(10, 120, 1000)['total_dose'], 1000)
        self.assertEqual(volume_for_dose(200, 100), 2)
        self.assertEqual(weight_based_total(5, 80, 300)['total_dose'], 300)
        self.assertEqual(weight_based_total(5, 80, 150)['total_dose'], 150)


if __name__ == '__main__':
    unittest.main()
