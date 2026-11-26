"""Source fidelity and population boundaries of the therapeutic projection."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import load_module
import therapeutic_plan_sources as sources


class TherapeuticPlanSources(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "references").mkdir()
        (self.root / "modules").mkdir()
        self.manifest = self.root / "references/module-index.md"
        self.manifest.write_text(
            "| Module ID | Bundle |\n|---|---|\n"
            "| adult-example | `modules/example.md` |\n"
            "| pediatric-example | `modules/example.md` |\n"
            "| mixed-example | `modules/example.md` |\n"
            "| heading-example | `modules/example.md` |\n"
            "| general-example | `modules/example.md` |\n", encoding="utf-8",
        )
        self.bundle = self.root / "modules/example.md"
        self.bundle.write_text(
            "# Synthetic reference fixture\n\nShared safety preamble: preserve this complete statement.\n\n"
            "## adult-example\n\n"
            "- Give the source medication dose ADULT_ONLY_AMOUNT.\n"
            "  Preserve its source restriction and contraindication.\n"
            "  - Nested source exception remains attached.\n\n"
            "- Monitor the stated source observations.\n"
            "- Reassess the stated source outcome.\n"
            "- Discharge only under the stated source conditions.\n\n"
            "## pediatric-example\n\n"
            "- Give the source medication dose CHILD_ONLY_AMOUNT.\n"
            "  The source-specific conditions remain attached.\n\n"
            "## mixed-example\n\n"
            "- Adult dose ADULT_ONLY_AMOUNT.\n"
            "- Pediatric dose CHILD_ONLY_AMOUNT.\n"
            "- Dose MIXED_AMOUNT for adults and children; do not split this paragraph.\n\n"
            "## heading-example\n\n"
            "### Adults\n\n- Give medication dose HEADING_ADULT_AMOUNT.\n\n"
            "### Children\n\n- Give medication dose HEADING_CHILD_AMOUNT.\n\n"
            "#### Reassessment\n\n- Reassess the child-specific source observation.\n\n"
            "### Other information\n\n- Give medication dose UNCLASSIFIED_AMOUNT.\n\n"
            "## general-example\n\n"
            "- Give medication dose GENERAL_AMOUNT; pediatric use needs a separate source.\n",
            encoding="utf-8",
        )
        self.patch = patch.object(sources, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_complete_reference_preamble_and_wrapped_safety_are_preserved(self):
        result = sources.build_reference("adult-example", "adult")
        self.assertEqual(result["reference_text"], load_module.load(self.root, "adult-example"))
        self.assertIn("Shared safety preamble: preserve this complete statement.", result["reference_text"])
        self.assertIn(
            "- Give the source medication dose ADULT_ONLY_AMOUNT.\n"
            "  Preserve its source restriction and contraindication.\n"
            "  - Nested source exception remains attached.", result["sections"]["medications"],
        )
        self.assertNotIn("CHILD_ONLY_AMOUNT", result["reference_text"])
        self.assertEqual(result["source_refs"], [{
            "module_id": "adult-example", "path": "clinical/modules/example.md",
            "sha256": hashlib.sha256(self.bundle.read_bytes()).hexdigest(), "language": "original",
        }])

    def test_population_specific_modules_cannot_be_copied_to_the_other_population(self):
        for module_id, population in (("adult-example", "pediatric"), ("pediatric-example", "adult"),
                                      ("general-example", "pediatric")):
            with self.subTest(module=module_id, population=population), self.assertRaises(ValueError):
                sources.build_reference(module_id, population)
        child = sources.build_reference("pediatric-example", "pediatric")
        self.assertIn("CHILD_ONLY_AMOUNT", child["sections"]["medications"])

    def test_mixed_reference_remains_complete_but_adult_dose_is_not_prefilled_for_children(self):
        child = sources.build_reference("mixed-example", "pediatric")
        adult = sources.build_reference("mixed-example", "adult")
        self.assertEqual(child["reference_text"], adult["reference_text"])
        self.assertIn("ADULT_ONLY_AMOUNT", child["reference_text"])
        self.assertIn("MIXED_AMOUNT", child["reference_text"])
        self.assertIn("CHILD_ONLY_AMOUNT", child["sections"]["medications"])
        self.assertNotIn("ADULT_ONLY_AMOUNT", child["sections"]["medications"])
        self.assertNotIn("MIXED_AMOUNT", child["sections"]["medications"])
        self.assertNotIn("CHILD_ONLY_AMOUNT", adult["sections"]["medications"])
        self.assertNotIn("MIXED_AMOUNT", adult["sections"]["medications"])
        self.assertNotEqual(child["source_revision"], adult["source_revision"])

    def test_explicit_subheading_scope_is_preserved_and_does_not_leak_to_next_heading(self):
        child = sources.build_reference("heading-example", "pediatric")
        text = "\n".join(child["sections"].values())
        self.assertIn("HEADING_CHILD_AMOUNT", text)
        self.assertIn("child-specific source observation", text)
        self.assertNotIn("HEADING_ADULT_AMOUNT", text)
        self.assertNotIn("UNCLASSIFIED_AMOUNT", text)

    def test_catalog_population_is_not_inferred_from_a_stray_child_mention(self):
        modules = {item["id"]: item for item in sources.catalog()["modules"]}
        self.assertEqual(modules["adult-example"]["populations"], ["adult"])
        self.assertEqual(modules["pediatric-example"]["populations"], ["pediatric"])
        self.assertEqual(modules["mixed-example"]["populations"], ["adult", "pediatric"])
        self.assertEqual(modules["heading-example"]["populations"], ["adult", "pediatric"])
        self.assertEqual(modules["general-example"]["populations"], ["adult"])
        self.assertTrue(all(item["source_language"] == "original" for item in modules.values()))

    def test_manual_reference_is_empty_and_cannot_claim_completeness(self):
        result = sources.build_reference(None, "adult")
        self.assertEqual(result["reference_text"], "")
        self.assertEqual(result["source_refs"], [])
        self.assertEqual(result["sections"], {name: "" for name in sources.SECTION_NAMES})
        self.assertTrue(all(any(name in text for text in result["missing_requirements"])
                            for name in sources.SECTION_NAMES))
        self.assertTrue(any("medication-selection-safety" in text for text in result["missing_requirements"]))

    def test_source_projection_always_retains_individualization_and_missing_section_requirements(self):
        result = sources.build_reference("adult-example", "adult")
        self.assertEqual(result["sections"]["initial_actions"], "")
        self.assertTrue(any("initial_actions" in text for text in result["missing_requirements"]))
        for requirement in sources.STANDARD_REQUIREMENTS:
            self.assertIn(requirement, result["missing_requirements"])
        self.assertNotIn("actionable", result)
        self.assertNotIn("reviewed", result)

    def test_revision_is_stable_and_changes_for_source_manifest_and_generator_changes(self):
        first = sources.build_reference("adult-example", "adult")["source_revision"]
        self.assertEqual(first, sources.build_reference("adult-example", "adult")["source_revision"])
        self.bundle.write_text(self.bundle.read_text() + "\nSource update.\n", encoding="utf-8")
        second = sources.build_reference("adult-example", "adult")["source_revision"]
        self.assertNotEqual(first, second)
        self.manifest.write_text(self.manifest.read_text() + "\nManifest update.\n", encoding="utf-8")
        third = sources.build_reference("adult-example", "adult")["source_revision"]
        self.assertNotEqual(second, third)
        with patch.object(sources, "GENERATOR_VERSION", "therapeutic-plan-sources/test-next"):
            self.assertNotEqual(third, sources.build_reference("adult-example", "adult")["source_revision"])

    def test_unknown_module_duplicate_heading_and_invalid_population_fail_closed(self):
        for module_id in ("../outside", "missing", "", True):
            with self.subTest(module=module_id), self.assertRaises(ValueError):
                sources.build_reference(module_id, "adult")
        for population in (None, "", "child", True):
            with self.subTest(population=population), self.assertRaises(ValueError):
                sources.build_reference(None, population)
        self.bundle.write_text(self.bundle.read_text() + "\n## adult-example\n\nDuplicate.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            sources.build_reference("adult-example", "adult")

    def test_concurrent_source_change_cannot_bind_old_text_to_a_new_hash(self):
        original_load = load_module.load

        def changing_load(root, module_id):
            text = original_load(root, module_id)
            self.bundle.write_text(self.bundle.read_text() + "\nConcurrent source update.\n", encoding="utf-8")
            return text

        with patch.object(load_module, "load", side_effect=changing_load), self.assertRaisesRegex(ValueError, "changed during"):
            sources.build_reference("adult-example", "adult")


class ExistingCanonicalTherapeuticSources(unittest.TestCase):
    def test_pediatric_asthma_retains_distinct_adolescent_short_course_reference(self):
        reference = sources.build_reference("pediatric-acute-asthma", "pediatric")
        medications = reference["sections"]["medications"]
        self.assertIn("Systemic corticosteroid 6--11 years", medications)
        self.assertIn("Systemic corticosteroid 12--17 years", medications)
        adolescent = next(
            paragraph for paragraph in medications.split("\n\n")
            if "Systemic corticosteroid 12--17 years" in paragraph
        )
        self.assertIn("40--50 mg PO once daily", adolescent)
        self.assertIn("5--7 days", adolescent)
        self.assertIn("age bands are alternatives", adolescent)
        self.assertIn("does not automatically select a dose", adolescent)
        self.assertIn("GINA 2026, Box 9-2", adolescent)

    def test_broad_catalogues_never_merge_their_regimens_into_one_case(self):
        modules = {item["id"]: item for item in sources.catalog()["modules"]}
        self.assertTrue(sources.REFERENCE_ONLY_MODULES <= modules.keys())
        for module_id in sources.REFERENCE_ONLY_MODULES:
            self.assertTrue(modules[module_id]["reference_only"])
            for population in modules[module_id]["populations"]:
                with self.subTest(module=module_id, population=population):
                    result = sources.build_reference(module_id, population)
                    self.assertTrue(result["reference_text"])
                    self.assertEqual(result["reference_text"], load_module.load(sources.ROOT, module_id))
                    self.assertTrue(result["source_refs"])
                    self.assertEqual(result["sections"], {name: "" for name in sources.SECTION_NAMES})
                    self.assertTrue(any("concrete pathology" in item for item in result["missing_requirements"]))

    def test_real_pediatric_module_and_both_population_reference_keep_canonical_text(self):
        for module_id, population in (("pediatric-acute-asthma", "pediatric"),
                                      ("acute-severe-asthma", "adult"), ("adrenal-crisis", "adult")):
            with self.subTest(module=module_id):
                reference = sources.build_reference(module_id, population)
                self.assertEqual(reference["reference_text"], load_module.load(sources.ROOT, module_id))
                self.assertTrue(reference["sections"]["medications"])
                self.assertNotIn(module_id, sources.REFERENCE_ONLY_MODULES)
        with self.assertRaises(ValueError):
            sources.build_reference("acute-severe-asthma", "pediatric")
        mixed = sources.build_reference("anaphylaxis", "pediatric")
        self.assertEqual(mixed["reference_text"], load_module.load(sources.ROOT, "anaphylaxis"))
        self.assertNotIn("adult dose", mixed["sections"]["medications"].lower())
        self.assertTrue(mixed["missing_requirements"])


if __name__ == "__main__":
    unittest.main()
