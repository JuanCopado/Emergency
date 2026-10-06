import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "procedure-v1.41.schema.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "data" / "procedures"
NEURO_IDS = [f"PROC-NEURO-{i:03d}" for i in range(1, 6)]

class NeurologyProcedureSchemaV141Tests(unittest.TestCase):
    def test_all_five_neurology_json_files_exist(self):
        for proc_id in NEURO_IDS:
            self.assertTrue((DATA_DIR / f"{proc_id}.json").exists(), proc_id)

    def test_required_top_level_fields_present(self):
        required = set(SCHEMA["required"])
        for proc_id in NEURO_IDS:
            data = json.loads((DATA_DIR / f"{proc_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(set(), required - set(data), proc_id)

    def test_safety_fields_are_nonempty_and_fail_closed(self):
        for proc_id in NEURO_IDS:
            data = json.loads((DATA_DIR / f"{proc_id}.json").read_text(encoding="utf-8"))
            self.assertEqual("YELLOW", data["status"], proc_id)
            self.assertTrue(data["stop_points"], proc_id)
            self.assertTrue(data["confirmation"], proc_id)
            self.assertTrue(data["rescue"], proc_id)
            self.assertTrue(data["documentation"], proc_id)
            self.assertTrue(data["sources"], proc_id)
            self.assertEqual("pending", data["qa"]["clinical_qa"], proc_id)
            self.assertEqual("paused", data["qa"]["visual_qa"], proc_id)
            self.assertTrue(data["qa"]["human_review_required"], proc_id)

    def test_step_order_is_contiguous(self):
        for proc_id in NEURO_IDS:
            data = json.loads((DATA_DIR / f"{proc_id}.json").read_text(encoding="utf-8"))
            orders = [x["order"] for x in data["steps"]]
            self.assertEqual(list(range(1, len(orders)+1)), orders, proc_id)

    def test_no_duplicate_neurology_ids(self):
        ids=[]
        for proc_id in NEURO_IDS:
            data=json.loads((DATA_DIR / f"{proc_id}.json").read_text(encoding="utf-8"))
            ids.append(data["procedure_id"])
        self.assertEqual(len(ids), len(set(ids)))

if __name__ == "__main__":
    unittest.main()
