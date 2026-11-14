"""High-risk source boundaries: age, CT triage, dose caps and escalation."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pediatric_burn_calculator import burn_plan


def module(module_id, bundle='special-populations'):
    text = (ROOT / f'modules/{bundle}.md').read_text()
    return re.search(r'^## ' + re.escape(module_id) + r'\n(.*?)(?=^## |\Z)', text, re.M | re.S)[1]


class TbiPediatricReferenceSafetyTests(unittest.TestCase):
    def test_observed_cohort_metrics_do_not_become_universal_npv_99(self):
        review = json.loads((ROOT / 'qa/TBI_AND_EIGHT_PEDIATRIC_REVIEW_2026-11-14.json').read_text())
        safety = review['biomarker_safety']; cohort = safety['cohort']
        self.assertEqual(sum(cohort[k] for k in ['true_positive', 'false_negative', 'true_negative', 'false_positive']), 970)
        self.assertAlmostEqual(100 * cohort['true_negative'] / (cohort['true_negative'] + cohort['false_negative']), 96.5156794425)
        self.assertAlmostEqual(100 * cohort['true_positive'] / (cohort['true_positive'] + cohort['false_negative']), 96.4664310954)
        self.assertFalse(safety['automatic_ct_avoidance'])
        self.assertFalse(safety['automatic_discharge'])
        self.assertFalse(safety['pediatric_adult_cutoff_extrapolation'])
        self.assertTrue(safety['same_cohort_not_independent_replication'])

    def test_biomarkers_do_not_override_adult_emergency_or_pediatric_age_gates(self):
        adult = module('traumatic-intracranial-mass-effect', 'neurologic')
        child = module('pediatric-head-injury')
        self.assertIn('a negative result cannot cancel urgent CT', adult)
        self.assertIn('age >=18', adult)
        self.assertIn('within 24 h', adult)
        self.assertIn('Ages **16--17**', child)
        self.assertIn('do not use adult GFAP/UCH-L1 or S100B thresholds', child)
        self.assertIn('Horta', adult)
        self.assertIn('5 mL/kg IV over 5--20 minutes', adult)

    def test_head_injury_escalation_includes_gcs_eight_and_two_point_fall(self):
        text = module('pediatric-head-injury')
        self.assertIn('persistent **GCS <=8**', text)
        self.assertIn('fall of >=2 GCS points', text)
        self.assertNotIn('persistent **GCS <8**', text)
        self.assertIn('not 1 or 0', text)
        self.assertIn('NT', text)

    def test_sedation_has_product_dependent_caps_rescue_and_recovery(self):
        text = module('pediatric-procedural-sedation')
        for anchor in ['100 micrograms', '75 micrograms', '300 micrograms/mL', 'capnography', 're-sedation', '3--5min', 'responsible adult']:
            self.assertIn(anchor, text)
        self.assertIn('after two doses', text)

    def test_hfno_checkpoints_never_delay_deterioration_response(self):
        text = module('pediatric-acute-respiratory-support')
        self.assertIn('not permission to wait', text)
        self.assertIn('not a reason to remove needed oxygen', text)
        self.assertIn('maximum **50 L/min**', text)
        self.assertIn('ready invasive-airway rescue plan', text)

    def test_infant_cns_doses_are_not_older_child_vancomycin(self):
        text = module('pediatric-cns-infection')
        self.assertIn('infants <=90 days require the infant-specific regimen', text)
        self.assertIn('>90 days with normal renal function', text)
        self.assertIn('max 2 g in this 0--2-month RCH table', text)
        self.assertIn('reference duration is **4 days**', text)
        self.assertIn('not the meningitis dose', text)

    def test_paracetamol_special_exposures_do_not_follow_single_ingestion_nomogram(self):
        text = module('pediatric-toxicology')
        self.assertIn('Do not use the nomogram for repeated supratherapeutic ingestion', text)
        self.assertIn('within 8 h', text)
        self.assertIn('modified-release', text.lower())
        self.assertIn('>2 times', text)
        self.assertIn('final infusion volume', text)

    def test_dka_retains_no_bolus_and_rapid_acting_overlap_boundary(self):
        text = module('pediatric-dka')
        for anchor in ['Do **not** give an insulin bolus', 'K <3.0', '30--60 min overlap is for the first rapid-acting SC dose', 'not a basal-only conversion rule', 'mannitol 20% 0.5 g/kg', '3% sodium chloride 3 mL/kg']:
            self.assertIn(anchor, text)

    def test_burn_arithmetic_is_an_initial_estimate_not_prior_fluid_accounting(self):
        # Independent worked case: 20kg,20% =>1200mL resuscitation,
        #600mL first phase,600mL second phase; maintenance1500mL/day.
        plan = burn_plan(20, 20, 4)
        self.assertEqual(plan['resuscitation_24h_ml'], 1200)
        self.assertEqual(plan['first_phase_rate_ml_h'], 150)
        self.assertEqual(plan['second_phase_rate_ml_h'], 37.5)
        self.assertEqual(plan['maintenance_ml_h'], 62.5)
        text = module('pediatric-burns')
        self.assertIn('no prior-fluid input', text)
        self.assertIn('not an exactly equal calculation', text)
        self.assertNotEqual(plan['maintenance_ml_h'], 4 * 10 + 2 * 10)

    def test_sepsis_resources_and_adrenal_ecg_do_not_create_unsafe_wait_gates(self):
        text = module('pediatric-sepsis')
        self.assertIn('do not give bolus fluid for sepsis without hypotension', text)
        self.assertIn('not the initial target', text)
        self.assertIn('DGS014/2018', text)
        text = module('pediatric-adrenal-crisis')
        self.assertIn('do not wait for both K >7 and ECG changes', text)
        self.assertIn('not a blend with different BSPED age bands', text)


if __name__ == '__main__':
    unittest.main()
