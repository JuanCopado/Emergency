"""A GREEN sodium reference cannot bypass product, correction or rescue gates."""
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from acute_medication_api import catalog,calculate_request

class SodiumReferenceClosureTests(unittest.TestCase):
    def payload(self,**changes):
        inputs=dict(population='adult',route='IV',indication_confirmed=True,allergy_contraindication_present=False,interaction_reviewed=True,monitoring_ready=True,local_protocol_verified=True,concentration=3,product_verified=True,symptoms_attributable=True,sodium_start_mmol_l=120,sodium_current_mmol_l=121,correction_window='first24',high_ods_risk=True,initial_response_reached=False,reassessment_ready=True)
        inputs.update(changes)
        return dict(regimen_id='sodium-hyponatremia',source_revision=catalog()['source_revision'],inputs=inputs)
    def test_finite_bolus_volume_and_rate_do_not_become_continuous_infusion(self):
        r=calculate_request(self.payload());self.assertFalse(r['blocked']);r=r['result']
        self.assertEqual(r['administration_volume_ml'],150);self.assertEqual(r['duration_min'],20)
        self.assertEqual(r['amount_per_hour'],150*60/20)
        self.assertEqual(r['amount_per_hour_unit'],'mL/h')
        self.assertIsNone(r['pump_ml_h'])
    def test_each_real_world_confirmation_remains_independent_of_green(self):
        row=next(x for x in catalog()['regimens'] if x['id']=='sodium-hyponatremia')
        self.assertEqual(row['source']['evidence']['status'],'green')
        for key in ['product_verified','local_protocol_verified','monitoring_ready','reassessment_ready']:
            with self.subTest(key=key):
                r=calculate_request(self.payload(**{key:False}));self.assertTrue(r['blocked']);self.assertNotIn('result',r)
                self.assertIn(key,[x['code'] for x in r['alerts']])
    def test_correction_ceiling_boundary_and_initial_response_stop_repetition(self):
        for risk,window,delta,blocked in [(True,'first24',7.9,False),(True,'first24',8,True),(False,'first24',9.9,False),(False,'first24',10,True),(False,'subsequent24',8,True)]:
            with self.subTest(risk=risk,window=window,delta=delta):
                r=calculate_request(self.payload(high_ods_risk=risk,correction_window=window,sodium_current_mmol_l=120+delta));self.assertEqual(r['blocked'],blocked)
        self.assertTrue(calculate_request(self.payload(initial_response_reached=True))['blocked'])
    def test_three_confirmed_recipe_sizes_preserve_mass_and_actual_final_volume(self):
        d=json.loads((ROOT/'qa/SODIUM_20PCT_MIXTURE_VERIFICATION_2026-11-14.json').read_text())
        for row in d['rows']:
            base=Decimal(str(row['base_0_9pct_remaining_ml']));stock=Decimal(str(row['stock_20pct_added_ml']));final=Decimal(str(row['final_volume_ml']))
            self.assertEqual(base+stock,final)
            self.assertEqual((base*Decimal('0.009')+stock*Decimal('0.2'))/final*100,Decimal('3.001'))
    def test_owner_availability_is_recorded_without_fabricating_independent_product_certificate(self):
        d=json.loads((ROOT/'qa/SODIUM_CLINICAL_REFERENCE_CLOSURE_2026-11-14.json').read_text())
        self.assertTrue(d['latest_owner_clarification']['local_nacl3_available'])
        self.assertEqual(d['clinical_reference_status'],'green')
        self.assertFalse(d['local_preparation_fully_validated']);self.assertFalse(d['ready_to_use_compound_certified'])
        text=(ROOT/'modules/renal-metabolic.md').read_text().split('## sodium-emergencies\n',1)[1].split('\n## ',1)[0]
        self.assertIn('never infuse water alone',text);self.assertIn('ordinary distilled water is not an IV product',text)
        self.assertIn('not a continuous450mL/h order',text)
    def test_new_adult_observational_evidence_does_not_become_randomized_or_pediatric_rule(self):
        text=(ROOT/'modules/renal-metabolic.md').read_text().split('## sodium-emergencies\n',1)[1].split('\n## ',1)[0]
        self.assertIn('not a randomized treatment trial',text)
        self.assertIn('substantial heterogeneity',text)
        self.assertIn('validate pediatric extrapolation',text)
        self.assertIn('draft/for review',text)

if __name__=='__main__':unittest.main()
