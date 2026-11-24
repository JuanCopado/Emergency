"""R25 · the synthetic driver is a pipeline smoke test, NOT the timed 30-stimuli dry run; and E1 (undeclared) is not F-Document (legacy bridge)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import bank_r23 as bank, dryrun  # noqa: E402

RESULT = dryrun.full_dry_run(resamples=300, count=4)
MANIFEST = RESULT["manifest"]
BY_ID = {s["stimulus_id"]: s for s in MANIFEST["stimuli"]}
BY_HASH = {s["sha256"]: s["stimulus_id"] for s in MANIFEST["stimuli"] if s["sha256"]}


class States(unittest.TestCase):
    def test_two_dry_run_states_are_kept_apart(self):
        self.assertEqual(RESULT["dry_run_type"], "SYNTHETIC_PIPELINE_SMOKE_TEST")
        full = RESULT["full_30_stimuli_timed_dry_run"]
        self.assertEqual(full["status"], "BLOCKED")
        joined = " ".join(full["reasons"])
        for needle in ("not generated", "not clinically adjudicated", "dedicated devices", "timed"):
            self.assertIn(needle, joined)

    def test_the_export_schema_is_not_changed_by_the_state_labels(self):
        self.assertNotIn("dry_run_type", RESULT["export"])
        self.assertEqual(RESULT["export"]["study_status"], "NOT_EXECUTED_PROTOCOL_ONLY")


class E1VersusDocument(unittest.TestCase):
    def test_manifest_entries(self):
        e1 = BY_ID["S2-14"]
        self.assertEqual((e1["scenario_code"], e1["true_modality"], e1["route_modality"], e1["expected_layer7_trigger"]),
                         ("E1", None, None, "T7-01_UNDECLARED_MODALITY"))
        self.assertEqual(e1["image_format"], "PDF")
        for sid in ("S1-13", "S2-13"):
            doc = BY_ID[sid]
            self.assertEqual((doc["scenario_code"], doc["route_modality"], doc["expected_layer7_trigger"]), ("F", "document", None))
            self.assertEqual(doc["mechanism_id"], "M3")

    def test_arm_b_blocks_e1_but_not_the_document_bridge(self):
        records, _ = dryrun.run(MANIFEST, count=4)
        seen = {"e1": 0, "doc": 0}
        for r in records:
            if r["arm"] != "B":
                continue
            sid = BY_HASH.get(r["stimulus_hash_sha256"])
            if sid == "S2-14":
                seen["e1"] += 1
                self.assertEqual(r["declared_envelope"]["selection_origin"], "none")
                self.assertEqual(r["outcome_status"], "blocked_by_layer7")
            elif sid in ("S1-13", "S2-13"):
                seen["doc"] += 1
                self.assertEqual(r["declared_envelope"]["selection_origin"], "legacy_document_bridge")
                self.assertIsNone(r["layer7_trigger_code"])
                self.assertEqual(r["outcome_status"], "completed")
        self.assertTrue(seen["e1"] and seen["doc"], seen)

    def test_arm_a_never_shows_layer7_for_either(self):
        records, _ = dryrun.run(MANIFEST, count=4)
        for r in records:
            if r["arm"] == "A":
                self.assertIsNone(r["layer7_trigger_code"])


if __name__ == "__main__":
    unittest.main()
