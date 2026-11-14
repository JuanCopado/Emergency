"""Do not turn inventory, owner intent or arithmetic into unsupported clearance."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from acid_base_hyperglycemia import calculate,MMHG_PER_KPA

class SelectedClosureSafetyTests(unittest.TestCase):
    def test_manual_gap_conventions_are_separate_from_unknown_local_profile(self):
        r=calculate(dict(sodium_mmol_l=140,chloride_mmol_l=100,hco3_mmol_l=20,potassium_mmol_l=4,albumin_g_l=40))
        self.assertEqual(r['anion_gap_mmol_l'],20)
        self.assertEqual(r['anion_gap_including_potassium_mmol_l'],24)
        self.assertEqual(r['albumin_corrected_anion_gap_mmol_l'],20)
        self.assertIn('not_a_verified_local',r['anion_gap_reference_source'])
    def test_winter_label_needs_confirmed_metabolic_component(self):
        d=dict(hco3_mmol_l=20,pco2_kpa=28/MMHG_PER_KPA)
        a=calculate(d);b=calculate({**d,'metabolic_acidosis_confirmed':True})
        self.assertNotIn('metabolic_acidosis_compensation',a)
        self.assertEqual(b['metabolic_acidosis_compensation'],'additional_respiratory_alkalosis')
        self.assertEqual(b['winters_expected_pco2_mm_hg']['low'],36)
        self.assertEqual(b['winters_expected_pco2_mm_hg']['high'],40)
    def test_inventory_does_not_claim_new_entry_by_entry_clinical_validation(self):
        d=json.loads((ROOT/'qa/NINE_SELECTED_MODULES_REVIEW_2026-11-14_INVENTORY.json').read_text())
        self.assertEqual(len(d['scales']),135);self.assertEqual(len(d['formulas']),45)
        self.assertEqual(len(d['pediatric_regimens']),89)
        self.assertTrue(all(x['source_url'] for x in d['scales']))
        self.assertTrue(all(x['product_portugal_match']=='not_newly_verified' for x in d['pediatric_regimens']))
        self.assertTrue(all(not x['automatic_pump_release'] for x in d['infusion_sheets']))
    def test_browser_failure_cannot_be_relabelled_pass(self):
        r=json.loads((ROOT/'qa/RESUSCITATION_ROUTER_BROWSER_2026-11-14.json').read_text())
        self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['cases_executed'],0)
        self.assertEqual(r['cases_planned'],8)
    def test_orthopedic_reference_preserves_limb_and_open_fracture_escalation(self):
        text=(ROOT/'modules/trauma-surgical.md').read_text().split('## orthopedic-emergencies\n',1)[1].split('\n## ',1)[0]
        for anchor in ['antibiotics immediately','Do not irrigate','Preserved pulses do not exclude compartment syndrome','first-line MRI','post-reduction neurovascular status']:
            self.assertIn(anchor,text)
    def test_unresolved_closure_gates_survive_explicit_general_green_request(self):
        r=json.loads((ROOT/'qa/NINE_SELECTED_MODULES_REVIEW_2026-11-14.json').read_text())
        outcomes={x['id']:x['after'] for x in r['modules']}
        for mid in ['arrhythmias-cardiac-arrest','sodium-emergencies','vasoactive-inotrope-infusions','icu-sedation-analgesia-infusions','clinical-scores-calculators','pediatric-outpatient-medications','clinical-note-diagnostic-support']:
            self.assertEqual(outcomes[mid],'yellow')
        self.assertEqual(r['clinical_release_status'],'CLINICALLY_PENDING')

if __name__=='__main__':unittest.main()
