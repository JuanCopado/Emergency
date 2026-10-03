#!/usr/bin/env python3
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from clinical_calculator import calculate, sum_components

class ClinicalScoresRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads((ROOT/"calculators"/"registry.json").read_text(encoding="utf-8"))

    def test_registry_unique_and_sized(self):
        scale_ids=[x["id"] for x in self.registry["scales"]]
        formula_ids=[x["id"] for x in self.registry["formulas"]]
        self.assertEqual(len(scale_ids), len(set(scale_ids)))
        self.assertEqual(len(formula_ids), len(set(formula_ids)))
        self.assertGreaterEqual(len(scale_ids),100)
        self.assertGreaterEqual(len(formula_ids),40)

    def test_every_entry_explains_measure_and_use(self):
        for item in self.registry["scales"] + self.registry["formulas"]:
            self.assertTrue(item.get("measures"))
            self.assertTrue(item.get("use"))
            self.assertTrue(item.get("editable"))

    def test_core_scale_ids_exist(self):
        ids={x["id"] for x in self.registry["scales"]}
        wanted={"nihss","abcd2","heart","wells-pe","perc","pesi","sofa",
                "news2","glasgow-coma","phoenix-sepsis","pecarn-head-injury"}
        self.assertTrue(wanted.issubset(ids))

    def test_common_emergency_formula_math(self):
        value,unit=calculate("map",{"SBP":90,"DBP":60})
        self.assertAlmostEqual(value,70.0)
        self.assertEqual(unit,"mmHg")
        value,_=calculate("anion-gap",{"Na":140,"Cl":104,"HCO3":18})
        self.assertAlmostEqual(value,18.0)
        value,_=calculate("pao2-fio2",{"PaO2_mmHg":80,"FiO2_fraction":0.5})
        self.assertAlmostEqual(value,160.0)
        value,_=calculate("mcgkgmin-to-mlh",{
            "dose_mcg_kg_min":0.1,"weight_kg":80,"concentration_mcg_mL":80})
        self.assertAlmostEqual(value,6.0)

    def test_pediatric_fluid_math(self):
        day,_=calculate("holliday-segar",{"weight_kg":25})
        rate,_=calculate("four-two-one",{"weight_kg":25})
        self.assertAlmostEqual(day,1600.0)
        self.assertAlmostEqual(rate,65.0)

    def test_fail_closed_on_missing_input(self):
        with self.assertRaises(ValueError):
            calculate("anion-gap",{"Na":140,"Cl":104})
        with self.assertRaises(ValueError):
            sum_components({"eye":4,"verbal":None,"motor":6})

    def test_component_sum_is_deterministic(self):
        self.assertEqual(sum_components({"eye":3,"verbal":3,"motor":4},3,15),10)

if __name__=="__main__":
    unittest.main()
