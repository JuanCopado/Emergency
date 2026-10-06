import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "modules" / "emergency-procedures-index.md"
FAMILY_DIR = ROOT / "modules" / "procedures"
ID_RE = re.compile(r"PROC-[A-Z]+-\d{3}")

class ProceduresCatalogTest(unittest.TestCase):
    def test_every_index_id_has_textual_family_card(self):
        index_ids = set(ID_RE.findall(INDEX.read_text(encoding="utf-8")))
        family_ids = set()
        for path in FAMILY_DIR.glob("*.md"):
            family_ids.update(ID_RE.findall(path.read_text(encoding="utf-8")))
        self.assertEqual(187, len(index_ids))
        self.assertEqual(index_ids, family_ids)

    def test_no_empty_family_files(self):
        files = sorted(FAMILY_DIR.glob("*.md"))
        self.assertEqual(16, len(files))
        for path in files:
            text = path.read_text(encoding="utf-8")
            self.assertGreater(len(text), 300, path.name)

    def test_visual_pipeline_is_fail_closed(self):
        status = (ROOT / "qa" / "V1.41_PROCEDURES_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("Clinical QA", status)
        self.assertIn("Visual QA", status)
        self.assertIn("no póster general multitécnica", status)

    def test_visual_brief_builder_covers_catalog(self):
        import importlib.util
        script = ROOT / "scripts" / "build_procedure_visual_briefs.py"
        spec = importlib.util.spec_from_file_location("visual_briefs", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cards = module.parse_cards()
        self.assertEqual(187, len(cards))
        self.assertEqual(187, len({item["procedure_id"] for item in cards}))
        self.assertTrue(all(item["image_status"] == "not_generated" for item in cards))

if __name__ == "__main__":
    unittest.main()
