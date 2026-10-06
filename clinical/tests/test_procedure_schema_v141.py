import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_procedure_schema_v141 import validate_template

class ProcedureSchemaV141Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / "schemas" / "procedure-v1.41.schema.json").read_text(encoding="utf-8"))
        cls.template = json.loads((ROOT / "templates" / "procedure-template-v1.41.json").read_text(encoding="utf-8"))

    def test_template_defaults_are_fail_closed(self):
        self.assertEqual([], validate_template(self.schema, self.template))
        self.assertEqual("YELLOW", self.template["status"])
        self.assertTrue(self.template["qa"]["human_review_required"])
        self.assertEqual("paused", self.template["qa"]["visual_qa"])

    def test_schema_requires_safety_and_confirmation(self):
        required = set(self.schema["required"])
        for field in ("stop_points", "confirmation", "rescue", "documentation", "sources", "qa"):
            self.assertIn(field, required)

    def test_schema_disallows_unexpected_top_level_fields(self):
        self.assertFalse(self.schema["additionalProperties"])

if __name__ == "__main__":
    unittest.main()
