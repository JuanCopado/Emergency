import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "audit_proc_schema",
    ROOT / "scripts" / "audit_procedure_schema_coverage_v141.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ProcedureSchemaCoverageV141Tests(unittest.TestCase):
    def test_catalog_has_197_canonical_procedures(self):
        cards = module.parse_cards()
        self.assertEqual(197, len(cards))
        self.assertEqual(197, len({c["procedure_id"] for c in cards}))

    def test_audit_is_fail_closed(self):
        card = {
            "procedure_id": "PROC-TEST-001",
            "title": "Test",
            "level": "CORE",
            "family_file": "x.md",
            "body": "**Objetivo:** ejemplo.",
        }
        result = module.audit_card(card)
        self.assertFalse(result["migration_ready"])
        self.assertIn("sources", result["missing_fields"])
        self.assertIn("steps", result["missing_fields"])
        self.assertEqual("YELLOW", result["status"])
        self.assertTrue(result["human_review_required"])

    def test_full_explicit_card_can_be_ready(self):
        body = """
**Objetivo:** x
**Indicaciones:** x
**Contraindicaciones / precauciones:** x
**Material:** x
**Anatomía:** x
**Preparación:** posición, asepsia
**Técnica:** x
**Confirmación:** x
**STOP:** x
**Complicaciones:** x
**Rescate:** x
**Después:** reevaluación
**Documentación:** x
**Fuentes:** ERC
"""
        card = {"procedure_id":"PROC-TEST-002","title":"Test","level":"CORE","family_file":"x.md","body":body}
        self.assertTrue(module.audit_card(card)["migration_ready"])

if __name__ == "__main__":
    unittest.main()
