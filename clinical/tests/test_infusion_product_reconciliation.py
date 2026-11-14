"""Product distinctions, dimensional checks and missing-data gates for17 sheets."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from load_module import load
from infusion_calculator import infusion_ml_h, fixed_dose_ml_h


class InfusionProductReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / 'qa/INFUSION_PRODUCT_RECONCILIATION_2026-11-14.json').read_text())
        cls.items = {x['drug']: x for x in cls.report['items']}

    def test_seventeen_distinct_sheets_do_not_release_unknown_preparations(self):
        self.assertEqual([x['number'] for x in self.report['items']], list(range(1, 18)))
        self.assertEqual(len(self.items), 17)
        for item in self.items.values():
            self.assertTrue(item['source_urls'])
            self.assertTrue(item['pending'])
            self.assertFalse(item['automatic_pump_release'])
        self.assertEqual(self.items['milrinone']['role_reported'], 'not_selected')
        self.assertEqual(self.items['ketamine']['role_reported'], 'not_selected')

    def test_norepinephrine_user_stock_is_base_half_of_bitartrate(self):
        findings = ' '.join(self.items['norepinephrine']['source_findings'])
        self.assertIn('0.5mg base/mL', findings)
        self.assertEqual(5 / 10, 25 / 50)
        #8mg BASE requires16mL of this declared stock, not8mL.
        self.assertEqual(8 / (5 / 10), 16)

    def test_manufacturer_08_reference_is_separate_from_local_one_unit_ml(self):
        row = self.items['vasopressin']['arithmetic_recipes'][0]
        self.assertEqual(row['drug_amount'], 40)
        self.assertEqual(row['final_volume_ml'], 50)
        self.assertEqual(row['concentration'], 0.8)
        for dose, rate in [(0.01, 0.75), (0.02, 1.5), (0.03, 2.25)]:
            self.assertAlmostEqual(fixed_dose_ml_h(dose * 60, row['concentration']), rate)
        text = load(ROOT, 'vasoactive-inotrope-infusions')
        self.assertIn('not a routine maximum imported from Vasostrict', text)
        self.assertIn('not the selected local pump table', text)
        self.assertEqual(self.items['vasopressin']['current_selected_preparation']['concentration_IU_ml'], 1)

    def test_catecholamine_and_inodilator_concentrations_have_independent_oracles(self):
        expected = {
            'epinephrine': [0.02, 0.1, 0.1],
            'dopamine': [0.8, 0.4, 4],
            'dobutamine': [1, 2, 5],
            'milrinone': [0.2, 0.2, 1],
            'phenylephrine': [0.1, 0.4],
            'angiotensin-ii': [0.005, 0.01, 0.01],
        }
        for drug, values in expected.items():
            self.assertEqual([x['concentration'] for x in self.items[drug]['arithmetic_recipes']], values)
        self.assertAlmostEqual(infusion_ml_h(20, 100, 0.375, 70)['ml_h'], 7.875)
        #Giapreza20ng/kg/min =0.020mcg/kg/min at5mcg/mL ->16.8mL/h.
        self.assertAlmostEqual(infusion_ml_h(2.5, 500, 0.020, 70)['ml_h'], 16.8)

    def test_sedative_strength_changes_cannot_reuse_same_pump_rate(self):
        expected = {'remifentanil': [0.05, 0.05, 0.05, 0.1],
                    'morphine': [0.5, 1, 1, 2],
                    'dexmedetomidine': [4, 4, 4, 8, 8, 8],
                    'midazolam': [1, 1, 2, 5], 'propofol': [10, 20]}
        for drug, values in expected.items():
            self.assertEqual([x['concentration'] for x in self.items[drug]['arithmetic_recipes']], values)
        self.assertAlmostEqual(infusion_ml_h(500, 50, 5, 70)['ml_h'], 2.1)
        self.assertAlmostEqual(infusion_ml_h(1000, 50, 5, 70)['ml_h'], 1.05)

    def test_uploaded_report_supplies_missing_recipes_without_releasing_them(self):
        #These four exact candidates came from the later attachment, not an invented standard.
        for drug, concentration in [('norepinephrine', 0.1), ('levosimendan', 0.05),
                                    ('hydromorphone', 0.2), ('ketamine', 1)]:
            item = self.items[drug]
            self.assertTrue(item['recipe_previously_missing_now_proposed'])
            self.assertEqual(item['protocol_followup']['concentration'], concentration)
            self.assertFalse(item['protocol_followup']['automatic_pump_release'])
        self.assertIn('80micrograms base/mL', ' '.join(self.items['phenylephrine']['source_findings']))

    def test_uploaded_standard_changes_require_actual_concentration_in_pump_math(self):
        self.assertEqual(len([x for x in self.items.values() if x.get('protocol_followup')]), 17)
        self.assertEqual(self.items['milrinone']['protocol_followup']['section_role_proposed'], 'reference_alternative')
        self.assertEqual(self.items['ketamine']['protocol_followup']['section_role_proposed'], 'reference_alternative')
        self.assertFalse(self.report['uploaded_protocol_followup']['original_modified'])
        self.assertRegex(self.report['uploaded_protocol_followup']['sha256'], r'^[0-9a-f]{64}$')
        self.assertAlmostEqual(infusion_ml_h(25, 250, 0.05, 70)['ml_h'], 2.1)
        #70kg at0.7mcg/kg/h gives49mcg/h: old10mcg/mL=4.9, proposed50mcg/mL=0.98.
        self.assertAlmostEqual(fixed_dose_ml_h(49, 10), 4.9)
        self.assertAlmostEqual(fixed_dose_ml_h(49, 50), 0.98)

    def test_label_scope_does_not_turn_into_blanket_24_or_48_hour_permission(self):
        self.assertIn('not generic24–48h', ' '.join(self.items['ketamine']['source_findings']))
        self.assertIn('no generic24h', ' '.join(self.items['epinephrine']['source_findings']))
        self.assertIn('does not import foreign-product dose or chemical-stability data',
                      ' '.join(self.items['vasopressin']['source_findings']))
        self.assertIn('diluted1% preparation maximum6h', ' '.join(self.items['propofol']['source_findings']))
        self.assertIn('not an injectable product source', ' '.join(self.items['hydromorphone']['source_findings']))
        self.assertIn('not to routinely offer opiates', ' '.join(self.items['morphine']['source_findings']))

    def test_owner_names_are_recorded_as_declared_not_independent_signatures(self):
        acceptance = self.report['local_acceptance']
        self.assertEqual(acceptance['clinical_reviewer'], 'Rui Susano')
        self.assertEqual(acceptance['pharmacy_reviewer'], 'Miguel S')
        self.assertEqual(acceptance['date'], '2026-11-14')
        self.assertIn('not independently authenticated', acceptance['provenance'])


if __name__ == '__main__':
    unittest.main()
