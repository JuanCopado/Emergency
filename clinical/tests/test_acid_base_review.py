"""Synthetic acid-base safety cases: units, gap conventions and conditional interpretation.

No patient record, identifier, laboratory signature or exact supplied case is stored.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from acid_base_hyperglycemia import calculate, MMHG_PER_KPA
from sodium_water_balance import calculate as water_balance


class AcidBaseReviewTests(unittest.TestCase):
    def test_equivalent_explicit_units_preserve_outputs(self):
        common = {'ph': 7.40, 'hco3_mmol_l': 15,
                  'sodium_mmol_l': 140, 'chloride_mmol_l': 105,
                  'fio2_fraction': 0.4, 'metabolic_acidosis_confirmed': True}
        a = calculate({**common, 'pco2_mm_hg': 25, 'pao2_mm_hg': 80,
                       'albumin_g_dl': 2})
        b = calculate({**common, 'pco2_kpa': 25 / MMHG_PER_KPA,
                       'pao2_kpa': 80 / MMHG_PER_KPA, 'albumin_g_l': 20})
        for key in ('anion_gap_mmol_l', 'albumin_corrected_anion_gap_mmol_l',
                    'delta_ratio', 'pao2_fio2_ratio_mm_hg',
                    'calculated_hco3_from_henderson_hasselbalch_mmol_l'):
            self.assertAlmostEqual(a[key], b[key])
        self.assertEqual(b['metabolic_acidosis_compensation'],
                         'additional_respiratory_alkalosis')

    def test_duplicate_unit_fields_are_rejected_even_if_equal(self):
        for a, b in [('pco2_mm_hg', 'pco2_kpa'),
                     ('pao2_mm_hg', 'pao2_kpa'),
                     ('albumin_g_dl', 'albumin_g_l')]:
            with self.subTest(a=a), self.assertRaisesRegex(ValueError, 'only one'):
                calculate({a: 1, b: 1})

    def test_gap_with_potassium_never_silently_changes_delta_convention(self):
        values = {'sodium_mmol_l': 140, 'chloride_mmol_l': 105,
                  'hco3_mmol_l': 15, 'potassium_mmol_l': 4}
        result = calculate(values)
        self.assertEqual(result['anion_gap_mmol_l'], 20)
        self.assertEqual(result['anion_gap_including_potassium_mmol_l'], 24)
        self.assertAlmostEqual(result['delta_ratio'], 8 / 9)
        self.assertIn('not_a_verified_local_interval',
                      result['anion_gap_reference_source'])
        self.assertEqual(result['delta_ratio_basis'],
                         'uncorrected_without_potassium_albumin_unknown')
        self.assertNotIn('albumin_corrected_anion_gap_mmol_l', result)
        custom = calculate({**values, 'anion_gap_reference_mmol_l': 8})
        self.assertAlmostEqual(custom['delta_ratio'], 12 / 9)

    def test_low_bicarbonate_alone_does_not_assert_a_mixed_diagnosis(self):
        result = calculate({'ph': 7.45, 'pco2_mm_hg': 30, 'hco3_mmol_l': 20})
        self.assertNotIn('metabolic_acidosis_compensation', result)
        self.assertIn('metabolic_acidosis_compensation_if_confirmed', result)
        self.assertIn('does not establish primary metabolic acidosis',
                      result['compensation_safety'])

    def test_normal_ph_does_not_hide_possible_triple_disorder(self):
        result = calculate({'ph': 7.40, 'pco2_mm_hg': 33.4, 'hco3_mmol_l': 20,
                            'sodium_mmol_l': 142, 'chloride_mmol_l': 94,
                            'metabolic_acidosis_confirmed': True})
        self.assertEqual(result['ph_state'], 'reference_range_or_mixed_disorder')
        self.assertEqual(result['delta_ratio'], 4)
        self.assertEqual(result['metabolic_acidosis_compensation'],
                         'additional_respiratory_alkalosis')
        self.assertIn('not a diagnosis by itself', result['delta_ratio_safety'])

    def test_delta_is_absent_with_no_high_gap_or_no_bicarbonate_deficit(self):
        for bicarbonate, chloride in [(24, 100), (28, 100), (20, 110)]:
            with self.subTest(bicarbonate=bicarbonate):
                result = calculate({'sodium_mmol_l': 140,
                                    'chloride_mmol_l': chloride,
                                    'hco3_mmol_l': bicarbonate})
                self.assertNotIn('delta_ratio', result)

    def test_impossible_and_nonfinite_inputs_are_rejected(self):
        for key, value in [('ph', 0), ('ph', 14), ('ph', 10**400),
                           ('ph', float('nan')), ('pco2_kpa', -1),
                           ('pco2_mm_hg', 0), ('hco3_mmol_l', -1),
                           ('sodium_mmol_l', 0), ('chloride_mmol_l', -1),
                           ('albumin_g_l', -1), ('potassium_mmol_l', -1),
                           ('anion_gap_reference_mmol_l', 0),
                           ('metabolic_acidosis_confirmed', 'yes')]:
            with self.subTest(key=key, value=str(value)[:20]), self.assertRaises(ValueError):
                calculate({key: value})

    def test_winter_boundaries_and_compensation_references(self):
        for pco2, expected in [(23, 'additional_respiratory_alkalosis'),
                               (24, 'appropriate_by_winters_formula'),
                               (28, 'appropriate_by_winters_formula'),
                               (29, 'additional_respiratory_acidosis')]:
            with self.subTest(pco2=pco2):
                result = calculate({'hco3_mmol_l': 12, 'pco2_mm_hg': pco2,
                                    'metabolic_acidosis_confirmed': True})
                self.assertEqual(result['metabolic_acidosis_compensation'], expected)
        self.assertEqual(calculate({'pco2_mm_hg': 50})[
            'respiratory_acidosis_expected_hco3_mmol_l'], {'acute': 25, 'chronic': 27.5})
        self.assertEqual(calculate({'pco2_mm_hg': 30})[
            'respiratory_alkalosis_expected_hco3_mmol_l'], {'acute': 22, 'chronic': 20})
        self.assertAlmostEqual(calculate({'hco3_mmol_l': 36})[
            'metabolic_alkalosis_expected_pco2_mm_hg']['center'], 48.4)

    def test_sodium_clearance_rejects_zero_and_oversized_denominator(self):
        for value in (0, 10**400):
            with self.subTest(value=str(value)[:20]), self.assertRaises(ValueError):
                water_balance({'serum_na_mmol_l': value, 'urine_na_mmol_l': 10,
                               'urine_k_mmol_l': 10, 'urine_volume_ml_h': 100})


if __name__ == '__main__':
    unittest.main()
