"""R21 · isolated Stage 1 laboratory (NO study executed): synthetic end-to-end, scenario identity, schema and PII checks."""
import json
import random
import re
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import human_factors_tools as hf  # noqa: E402

LAB = ROOT / "qa" / "human-factors" / "stage1"
SCHEMA = ROOT / "references" / "human-factors-export.schema.json"
MANIFEST = json.loads((LAB / "manifest.example.json").read_text(encoding="utf-8"))
PLATFORM_OF = {"set1": "web", "set2": "mobile"}


def synthetic_records(participants=12, seed="lab"):
    """Fully synthetic trials: one condition per period, banks counterbalanced, opaque participant codes."""
    codes = [f"HF1-P{i:03d}" for i in range(1, participants + 1)]
    allocation = hf.assign_sequences(codes, seed)["allocation"]
    rng = random.Random(f"{seed}:records")
    rows = []
    for index, code in enumerate(codes):
        slot = allocation[code]
        banks = ("set1", "set2") if index % 2 == 0 else ("set2", "set1")
        for period, (condition, bank) in enumerate(((slot["period1"], banks[0]), (slot["period2"], banks[1])), start=1):
            scenes = [s for s in MANIFEST["scenarios"] if s["bank_set"] == bank]
            for order, scene in enumerate(scenes, start=1):
                wrong_probability = 0.12 if condition == "baseline" else 0.05
                intended = scene["intended_modality"]
                chosen = rng.choice([m for m in hf.MODALITIES if m != intended]) if rng.random() < wrong_probability else intended
                rows.append({"participant": code, "role": rng.choice(hf.ROLES), "scenario_id": scene["scenario_id"], "condition": condition,
                             "period": period, "intended_modality": intended, "initial_modality": chosen, "chosen_modality": chosen,
                             "confirmed": True, "changed_modality_count": 0, "seconds": round(rng.uniform(8, 25), 2),
                             "comprehension_correct": rng.random() < 0.8, "platform": PLATFORM_OF[bank], "order_in_period": order})
    return rows


class ScenarioIdentity(unittest.TestCase):
    def test_the_example_manifest_is_valid_synthetic_and_not_frozen(self):
        out = hf.validate_manifest(MANIFEST)
        self.assertEqual((out["scenarios"], out["banks"]), (10, ["set1", "set2"]))
        self.assertFalse(out["stimuli_frozen"])           # an example has no frozen stimuli
        self.assertTrue(all(s["synthetic"] is True for s in MANIFEST["scenarios"]))

    def test_banks_are_disjoint_and_stimulus_hashes_are_unique_and_well_formed(self):
        good = dict(MANIFEST["scenarios"][0])
        other = dict(MANIFEST["scenarios"][1])
        base = {"manifest_version": "v1"}
        hf.validate_manifest(dict(base, scenarios=[dict(good, stimulus_sha256="a" * 64), dict(other, stimulus_sha256="b" * 64)]))
        frozen = hf.validate_manifest(dict(base, scenarios=[dict(good, stimulus_sha256="a" * 64), dict(other, stimulus_sha256="b" * 64)]))
        self.assertTrue(frozen["stimuli_frozen"])
        for bad in (dict(base, scenarios=[dict(good, stimulus_sha256="a" * 64), dict(other, stimulus_sha256="a" * 64)]),      # same hash
                    dict(base, scenarios=[dict(good, stimulus_sha256="A" * 64)]),                                              # upper case
                    dict(base, scenarios=[dict(good, stimulus_sha256="a" * 63)]),
                    dict(base, scenarios=[dict(good, bank_set="set3")]),
                    dict(base, scenarios=[good, dict(other, case_code=good["case_code"], bank_set="set2" if good["bank_set"] == "set1" else "set1")])):  # case in both banks
            with self.assertRaises(ValueError):
                hf.validate_manifest(bad)

    def test_a_record_must_match_the_scenario_identity(self):
        rows = synthetic_records(2)
        hf.check_records_against_manifest(rows, MANIFEST)
        wrong = dict(rows[0], intended_modality="document" if rows[0]["intended_modality"] != "document" else "ecg")
        with self.assertRaises(ValueError):
            hf.check_records_against_manifest([wrong], MANIFEST)


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = synthetic_records(12)
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(cls.schema)

    def test_the_synthetic_pipeline_runs_from_assignment_to_a_validated_reproducible_export(self):
        self.assertEqual(hf.validate_records(self.rows), len(self.rows))
        package = {"manifest": MANIFEST, "records": self.rows}
        first = hf.export_package(package, resamples=300, seed="e2e", git_commit_sha="abcdef1")
        second = hf.export_package(package, resamples=300, seed="e2e", git_commit_sha="abcdef1")
        self.assertEqual(first, second)
        jsonschema.Draft202012Validator(self.schema).validate(json.loads(json.dumps(first)))
        design = first["summary"]["design"]
        self.assertEqual((design["participants"], design["participants_with_both_conditions"]), (12, 12))
        self.assertEqual(design["sequences"], {"AB": 6, "BA": 6})
        self.assertTrue(design["small_cluster_warning"])
        self.assertEqual(first["study_status"], "NOT_EXECUTED_TOOLING_ONLY")

    def test_the_default_analysis_uses_at_least_5000_resamples_and_validates(self):
        full = hf.export_package({"manifest": MANIFEST, "records": self.rows}, seed="full")
        self.assertGreaterEqual(full["bootstrap_replicates"], 5000)
        self.assertEqual(full["summary"]["design"]["resamples"], full["bootstrap_replicates"])
        jsonschema.Draft202012Validator(self.schema).validate(json.loads(json.dumps(full)))

    def test_the_export_schema_rejects_a_study_claim_a_verdict_or_a_pretest(self):
        good = hf.export_package({"manifest": MANIFEST, "records": self.rows}, resamples=50, seed="s")
        validator = jsonschema.Draft202012Validator(self.schema)
        validator.validate(json.loads(json.dumps(good)))
        for mutate in (lambda d: d.update(study_status="EXECUTED"), lambda d: d["summary"].update(acceptance_decision="PASS"),
                       lambda d: d["summary"].update(sample_size=40), lambda d: d["summary"].update(acceptance_margin=0.05),
                       lambda d: d["summary"]["crossover_and_device_models"].update(carryover_pretest="PERFORMED"),
                       lambda d: d.update(git_commit_sha="not-a-sha"), lambda d: d.update(extra="x"),
                       lambda d: d.pop("dataset_sha256"), lambda d: d["summary"]["design"].update(independence_of_trials="ASSUMED")):
            bad = json.loads(json.dumps(good))
            mutate(bad)
            self.assertFalse(validator.is_valid(bad))

    def test_the_captured_records_carry_only_closed_values_and_opaque_codes(self):
        self.assertEqual({k for r in self.rows for k in r}, hf.FIELDS)
        for row in self.rows:
            self.assertRegex(row["participant"], r"^HF1-P\d{3}$")
            self.assertRegex(row["scenario_id"], hf.CODE.pattern)
            for field in ("role", "condition", "intended_modality", "initial_modality", "chosen_modality", "platform"):
                self.assertIsInstance(row[field], str)
            self.assertIn(row["role"], hf.ROLES)

    def test_the_arms_are_balanced_and_each_scenario_is_seen_in_one_period_only(self):
        seen = {}
        for row in self.rows:
            key = (row["participant"], row["scenario_id"])
            self.assertNotIn(key, seen)               # no scenario repeated for a participant across periods
            seen[key] = row["condition"]
        self.assertEqual(self.rows[0]["scenario_id"] in {s["scenario_id"] for s in MANIFEST["scenarios"]}, True)
        by_condition = {c: sum(r["condition"] == c for r in self.rows) for c in hf.CONDITIONS}
        self.assertEqual(by_condition["baseline"], by_condition["prototype"])


class NoPersonalData(unittest.TestCase):
    PATTERNS = {"email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "phone": re.compile(r"(?<!\w)\+?\d[\d ().-]{8,}\d(?!\w)"),
                "url": re.compile(r"https?://"), "national_id": re.compile(r"\b\d{8}[A-Za-z]\b"), "image": re.compile(r"\.(png|jpe?g|webp|dcm|gif)\b", re.I)}

    def test_the_laboratory_directory_and_the_example_hold_no_personal_data_or_images(self):
        files = [p for p in LAB.rglob("*") if p.is_file()]
        self.assertTrue(files)
        for path in files:
            self.assertNotIn(path.suffix.lower(), {".png", ".jpg", ".jpeg", ".webp", ".dcm", ".gif", ".pdf", ".zip"}, str(path))
            text = path.read_text(encoding="utf-8")
            for name, pattern in self.PATTERNS.items():
                if path.name == "README.md" and name == "image":
                    continue   # the README names the forbidden extensions in prose
                self.assertIsNone(pattern.search(text), (str(path), name))

    def test_the_lab_is_not_wired_into_the_product(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            if path.name != "human_factors_tools.py":
                text = path.read_text(encoding="utf-8", errors="ignore")
                self.assertNotIn("human-factors-export", text, str(path))
                self.assertNotIn("manifest.example.json", text, str(path))


if __name__ == "__main__":
    unittest.main()
