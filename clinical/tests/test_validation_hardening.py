import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


CLINICAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = CLINICAL_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_script(name: str):
    path = CLINICAL_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATE = load_script("validate_modules")
AUDIT = load_script("audit_evidence_coverage")


class ValidationHardeningTests(unittest.TestCase):
    def test_current_evidence_windows_have_no_expired_green(self):
        result = AUDIT.audit(CLINICAL_ROOT, today=date(2026, 10, 2))
        stale_green = [
            item for item in result["errors"]
            if "green cannot remain current past its review window" in item
        ]
        self.assertEqual(stale_green, [])

    def test_future_audit_detects_expired_green(self):
        result = AUDIT.audit(CLINICAL_ROOT, today=date(2027, 1, 31))
        self.assertTrue(
            any(
                "green cannot remain current past its review window" in item
                for item in result["errors"]
            )
        )

    def test_duplicate_manifest_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "modules").mkdir()
            (root / "references" / "module-index.md").write_text(
                "| Module ID | Bundle |\n"
                "|---|---|\n"
                "| alpha-module | `modules/a.md` |\n"
                "| alpha-module | `modules/a.md` |\n",
                encoding="utf-8",
            )
            (root / "references" / "router.md").write_text(
                "- alpha -> alpha-module\n", encoding="utf-8"
            )
            (root / "modules" / "a.md").write_text(
                "## alpha-module\n", encoding="utf-8"
            )
            _, errors = VALIDATE.validate(root)
            self.assertTrue(
                any("duplicate module IDs in manifest" in item for item in errors)
            )

    def test_router_uses_exact_module_id_boundaries(self):
        self.assertTrue(VALIDATE._contains_exact_module(" -> dvt + pulmonary-embolism", "dvt"))
        self.assertFalse(VALIDATE._contains_exact_module(" -> adult-dvt-route", "dvt"))


if __name__ == "__main__":
    unittest.main()
