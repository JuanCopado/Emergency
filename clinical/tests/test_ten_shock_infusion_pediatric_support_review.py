"""Safety boundaries and dimensional checks for the ten support references."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load
from infusion_calculator import infusion_ml_h, fixed_dose_ml_h, weight_per_hour_ml_h
from pediatric_emergency_calculator import (
    weight_based_total, volume_for_dose, infusion_per_kg_hour_ml_h,
    maintenance_ml_day, maintenance_ml_h, fluid_bolus_ml,
)


class SupportReviewTests(unittest.TestCase):
    def text(self, module):
        return ' '.join(load(ROOT, module).split())

    def test_undifferentiated_shock_does_not_inherit_sepsis_orders(self):
        text = self.text('undifferentiated-shock')
        self.assertIn('not every undifferentiated shock', text)
        self.assertIn('rather than a static pressure or lactate alone', text)

    def test_pediatric_shock_preserves_uncertainty_and_resource_condition(self):
        text = self.text('pediatric-shock')
        self.assertIn('selected ERC 2025 pathway', text)
        self.assertIn('insufficient to mandate starting vasoactives before versus after 40 mL/kg', text)
        self.assertIn('without intensive-care availability', text)
        self.assertIn('not a mandatory volume to complete', text)

    def test_vasoactive_arithmetic_does_not_certify_compatibility(self):
        text = self.text('vasoactive-inotrope-infusions')
        self.assertIn('Preparation review 14 November 2026 — YELLOW', text)
        self.assertIn('physicochemical stability separately from microbiological', text)
        self.assertIn('base-versus-salt expression', text)

    def test_sedation_does_not_apply_common_hang_time(self):
        text = self.text('icu-sedation-analgesia-infusions')
        self.assertIn('Preparation review 14 November 2026 — YELLOW', text)
        self.assertIn('a common 24-hour replacement rule is not established', text)

    def test_pediatric_drug_frame_does_not_underdose_when_cpr_required(self):
        text = self.text('pediatric-emergency-medications')
        self.assertIn('start CPR and use adrenaline **10 micrograms/kg IV/IO, max 1 mg**', text)
        self.assertIn('do not substitute it once compressions are indicated', text)
        self.assertIn('does not revalidate every entry', text)

    def test_fluids_do_not_interchange_hypertonic_percentages(self):
        text = self.text('pediatric-iv-fluid-therapy')
        self.assertIn('Do not substitute the same mL/kg or the same 100 mL cap', text)
        self.assertIn('4/2/1 hourly approximation are not identical', text)

    def test_asthma_uses_2026_age_and_severity_targets(self):
        text = self.text('pediatric-acute-asthma')
        self.assertIn('**92--95% for children 6--11 years**', text)
        self.assertIn('**4--6 puffs** for moderate attacks', text)
        self.assertIn('**6--10 puffs** for severe/life-threatening attacks', text)
        self.assertIn('not targets for arrest', text)

    def test_airway_keeps_named_source_and_post_paralysis_safety(self):
        text = self.text('pediatric-airway-rsi')
        self.assertIn('rocuronium **1.2--1.6 mg/kg IV**', text)
        self.assertNotIn('A separate 2025 national pediatric protocol', text)
        self.assertIn('suggests against etomidate', text)
        self.assertIn('paralysis can outlast induction', text)

    def test_electrolytes_retain_glucose_hyponatraemia_and_line_caveats(self):
        text = self.text('pediatric-electrolyte-emergencies')
        self.assertIn('**if no hyponatraemia**', text)
        self.assertIn('not directly from a concentrated vial', text)
        self.assertIn('not interchangeable mL-for-mL', text)
        self.assertIn('Sum potassium from all infusions', text)

    def test_blood_does_not_transfer_txa_loading_cap_or_guess_boundary_weights(self):
        for mid in ['pediatric-blood-transfusion-major-hemorrhage', 'pediatric-emergency-medications']:
            self.assertNotIn('**2 mg/kg/h, max 1 g**', self.text(mid))
        text = self.text('pediatric-blood-transfusion-major-hemorrhage')
        self.assertIn('At exactly 20 kg (RBC) or 15 kg (platelets)', text)
        self.assertIn('from the product leaving the blood bank', text)

    def test_norepinephrine_concentration_change_halves_rate(self):
        # 70kg *0.05mcg/kg/min =3.5mcg/min. 8mg/200mL vs100mL.
        dilute = infusion_ml_h(8, 200, 0.05, 70)
        concentrated = infusion_ml_h(8, 100, 0.05, 70)
        self.assertEqual(dilute['concentration_mcg_ml'], 40)
        self.assertAlmostEqual(dilute['ml_h'], 5.25)
        self.assertAlmostEqual(concentrated['ml_h'], 2.625)

    def test_fixed_units_minute_and_weight_units_hour_do_not_mix(self):
        self.assertAlmostEqual(fixed_dose_ml_h(0.03 * 60, 1), 1.8)
        self.assertAlmostEqual(weight_per_hour_ml_h(0.7, 70, 4), 12.25)
        # Propofol5mcg/kg/min =0.3mg/kg/h; 1% =10mg/mL.
        self.assertAlmostEqual(infusion_ml_h(1000, 100, 5, 70)['ml_h'], 2.1)

    def test_pediatric_dose_caps_and_maintenance_txa_use_different_units(self):
        self.assertEqual(weight_based_total(20, 60, 1000)['total_dose'], 1000)
        self.assertEqual(weight_based_total(0.1, 20, 10)['total_dose'], 2)
        self.assertEqual(volume_for_dose(2, 1), 2)
        # Synthetic verified-input example, not a new TXA preparation.
        self.assertEqual(infusion_per_kg_hour_ml_h(2, 20, 10), 4)

    def test_fluid_daily_hourly_boundary_is_explicit(self):
        self.assertEqual(fluid_bolus_ml(12, 10), 120)
        self.assertEqual(maintenance_ml_day(25), 1600)
        self.assertAlmostEqual(maintenance_ml_h(25), 1600 / 24)
        self.assertNotEqual(maintenance_ml_h(25), 4 * 10 + 2 * 10 + 5)


if __name__ == '__main__':
    unittest.main()
