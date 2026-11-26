"""Source fidelity and clinical boundary checks for the corticosteroid consultation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "clinical/scripts"))
from build_corticosteroid_catalog import SOURCE, OUTPUT, build_catalog, rendered_catalog


class CorticosteroidCatalogTests(unittest.TestCase):
    def test_projection_is_current_and_has_canonical_fingerprint(self):
        projected = json.loads(OUTPUT.read_text())
        self.assertEqual(OUTPUT.read_text(), rendered_catalog())
        self.assertEqual(projected["source_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())

    def test_reference_tables_preserve_the_published_discrepancy(self):
        data = build_catalog()
        values = {table["id"]: {row["drug_id"]: row["equivalent_mg"] for row in table["rows"]} for table in data["tables"]}
        self.assertEqual(values["endotext-2018"]["dexamethasone"], 0.75)
        self.assertEqual(values["ese-es-2024"]["dexamethasone"], 0.5)
        self.assertEqual(values["endotext-2018"]["betamethasone"], 0.6)
        self.assertEqual(values["ese-es-2024"]["betamethasone"], 0.5)
        self.assertEqual(data["scope"]["supported_routes"], ["oral", "iv"])
        self.assertIn("pediatric_weight_based_dose", data["scope"]["not_equivalent"])

    def test_each_link_reuses_an_existing_module(self):
        data = build_catalog()
        index = (ROOT / "clinical/references/module-index.md").read_text()
        ids = [data["module_id"], data["short_courses"]["bell_palsy"]["module_id"]] + [row["id"] for row in data["related_modules"]]
        for ident in ids:
            with self.subTest(module=ident):
                self.assertIn("| " + ident + " |", index)

    def test_rejects_duplicate_or_incomplete_table_rows(self):
        data = json.loads(SOURCE.read_text())
        data["tables"][0]["rows"][1] = data["tables"][0]["rows"][0]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "catalog.json"
            source.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "exactly once"):
                build_catalog(source)

    def test_pediatric_reference_is_the_existing_crisis_schedule(self):
        data = build_catalog()["hydrocortisone"]
        pediatric = data["pediatric_adrenal_crisis"]
        self.assertEqual([(row["initial_mg"], row["maintenance_mg"]) for row in pediatric["rows"]],
                         [(25, [5, 10]), (25, [10, 10]), (50, [12.5, 12.5]), (50, [25, 25]), (100, [25, 25])])
        self.assertIn("2026-11-14", pediatric["existing_acceptance"])
        self.assertEqual(data["adult_adrenal_crisis"]["maintenance_alternative_mg"], 50)
        self.assertEqual(data["pediatric_septic_shock"]["source_ids"], ["ssc-pediatric-2026"])

    def test_bell_reference_preserves_trial_and_separate_pediatric_boundary(self):
        bell = build_catalog()["short_courses"]["bell_palsy"]
        self.assertEqual((bell["module_id"], bell["section_id"]), ("ent-emergencies", "bell-palsy"))
        self.assertEqual((bell["guideline_min_age_years"], bell["adult_draft_min_age_years"], bell["onset_window_hours"]), (16, 18, 72))
        self.assertEqual(bell["reference_regimen"], {
            "drug_id": "prednisolone", "dose_mg": 25, "route": "oral", "interval_hours": 12,
            "duration_days": 10, "total_mg_per_day": 50, "source_id": "sullivan-bell-2007",
        })
        self.assertIn("sin prellenar una pauta adulta", bell["pediatric_es"])
        self.assertIn("no descartan ictus", bell["differential_es"])
        self.assertIn("bellpic-2022", bell["source_ids"])
        self.assertNotIn("pediatric_regimen", bell)

    def test_bell_cannot_drop_source_or_expand_adult_draft_to_a_child(self):
        for field, value in (("adult_draft_min_age_years", 17), ("source_ids", ["unverified-source"])):
            data = json.loads(SOURCE.read_text())
            data["short_courses"]["bell_palsy"][field] = value
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "catalog.json"
                source.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    build_catalog(source)


if __name__ == "__main__":
    unittest.main()
