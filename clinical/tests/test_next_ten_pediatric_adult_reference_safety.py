"""Regression gates for source versions, emergency triage and dose-unit boundaries."""
import re
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pediatric_hypertension_calculator import labetalol_ml_h,hydralazine_ml_h

def body(mid):
    for p in (ROOT/'modules').glob('*.md'):
        m=re.search(r'^## '+mid+r'\n(.*?)(?=^## |\Z)',p.read_text(),re.M|re.S)
        if m:return m[1]
    raise AssertionError(mid)

class NextTenSafetyTests(unittest.TestCase):
    def test_abdominal_emergencies_do_not_use_negative_bedside_scan_for_clearance(self):
        s=body('pediatric-abdominal-surgical-emergencies')
        self.assertIn('negative bedside POCUS does not exclude',s)
        self.assertIn('surgical backup',s)
        self.assertIn('not automatic after technical success',s)
    def test_trauma_loading_cap_is_not_whole_course_cap(self):
        s=body('pediatric-major-trauma')
        self.assertIn('do not extend the loading-dose cap to the whole treatment course',s)
        self.assertIn('rather than repeating crystalloid',s)
    def test_pump_examples_have_independent_mg_microgram_and_minute_conversion(self):
        self.assertEqual(labetalol_ml_h(10,0.25,1),2.5)
        self.assertEqual(labetalol_ml_h(10,0.25,5),0.5)
        self.assertEqual(hydralazine_ml_h(10,4,400),6)
    def test_pediatric_antihypertensive_daily_caps_and_product_limits_remain_visible(self):
        s=body('pediatric-hypertensive-emergency')
        for a in ['capped60mg/day','initial-rate ceiling','6h room-temperature','no faster than10mg/min','prepared immediately before use']:
            self.assertIn(a,s)
    def test_battery_mitigation_never_delays_removal_and_ct_is_selected(self):
        s=body('pediatric-foreign-body-emergencies')
        self.assertIn('selected low-dose CT',s)
        self.assertIn('not delay bronchoscopy when clinical suspicion is high',s)
        self.assertNotIn('CT is not routinely recommended',s)
        self.assertIn('swallowing is safe',s)
        self.assertIn('not a permissible wait',s)
    def test_hypothermic_pediatric_schedule_is_not_adult_schedule(self):
        s=body('pediatric-drowning-hypothermia')
        self.assertIn('Do not import the different adult hypothermia',s)
        self.assertIn('not an instruction to induce hypothermia in every drowning child',s)
    def test_oncology_does_not_mandate_fluid_boluses_or_replace_missing_g6pd(self):
        s=body('pediatric-hematology-oncology-emergencies')
        self.assertIn('not a mandatory bolus sequence',s)
        self.assertIn('do not treat unknown G6PD status as a negative test',s)
        self.assertIn('asymptomatic hypocalcaemia is not an automatic',s)
    def test_upper_gi_reconciles_new_variceal_and_clot_reference_without_fixed_restart_day(self):
        s=body('upper-gi-bleeding')
        for a in ['Baveno VIII2026','ESGE2026 suggests clot removal','no universal restart day','Monitor sodium with terlipressin']:
            self.assertIn(a,s)
    def test_aki_draft_is_not_presented_as_final_and_creatinine_is_not_sole_dialysis_gate(self):
        s=body('aki-nephrology')
        self.assertIn('public-review draft',s)
        self.assertIn('published KDIGO2012 baseline',s)
        self.assertIn('without a creatinine-only threshold',s)
        self.assertIn('do not use low-dose dopamine',s)
    def test_dermatology_and_device_require_syndrome_and_device_specific_rescue(self):
        s=body('dermatology-severe')
        self.assertIn('not transfer adult regimens automatically to children',s)
        self.assertIn('Do not delay emergency antibiotics/surgery',s)
        s=body('device-complications')
        self.assertIn('ensure therapies are restored',s)
        self.assertIn('without changing pacing',s)
        self.assertIn('do not attempt bedside lead removal',s)

if __name__=='__main__':unittest.main()
