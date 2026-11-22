"""R8 · proposed (inactive) contracts and the frozen synthetic corpus.

Checks integrity, structure and that nothing is wired into the product. It deliberately does NOT
assert that paraphrases are detected: labels are engineering construction, not adjudication.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_r8_reassurance_baseline as baseline  # noqa: E402

SCHEMA = ROOT / "references" / "skin-wound-phase1-contract.proposed.json"
SIGNS = ("chromatic_alteration", "exudate_compatible_surface_material", "necrotic_appearing_tissue",
         "visible_edge_separation", "apparent_deep_structure_exposure")


def valid_document(**changes):
    sign = {"state": "not_observable"}
    doc = {"contract_version": "phase1-0.2-proposed",
           "modality": {"kind_effective": "other_image", "kind_source": "default_unclassified",
                        "modality_verification": "not_verified", "kind_discordance": "unknown",
                        "kind_explicit": None, "kind_inferred": None},
           "observations": {name: dict(sign) for name in SIGNS},
           "abstention": {"decision": "none", "reason_codes": []},
           "provenance": "provider_structured",
           "human_review_reasons": ["modality_not_verified", "phase1_clause_required"],
           "fixed_clause_id": "phase1-anti-exclusion-v0"}
    doc.update(changes)
    return doc


class FrozenCorpus(unittest.TestCase):
    def test_hash_is_pinned_and_content_is_synthetic_and_stratified(self):
        corpus, digest = baseline.load()
        self.assertEqual(digest, hashlib.sha256(baseline.CORPUS.read_bytes()).hexdigest())
        self.assertEqual(corpus["status"], "UNADJUDICATED_ENGINEERING_DRAFT")
        self.assertEqual(corpus["clinical_status"], "CLINICALLY_PENDING")
        ids = [case["id"] for case in corpus["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        for case in corpus["cases"]:
            self.assertIn(case["lang"], corpus["languages"])
            self.assertIn(case["class"], corpus["classes"])
            self.assertIn(case["label"], corpus["labels"])
        for lang in corpus["languages"]:
            for cls in corpus["classes"]:
                self.assertTrue(any(c["lang"] == lang and c["class"] == cls for c in corpus["cases"]),
                                (lang, cls))

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "corpus.json"
            copy.write_bytes(baseline.CORPUS.read_bytes() + b" ")
            with self.assertRaises(SystemExit):
                baseline.load(copy, baseline.PIN)

    def test_encoding_variants_are_intercepted_by_the_shipped_filter(self):
        corpus, _ = baseline.load()
        variants = [c for c in corpus["cases"] if c["class"] == "unicode_variant"]
        self.assertTrue(variants)
        for case in variants:
            with self.subTest(case=case["id"]):
                self.assertTrue(baseline.intercepted(case["text"]), case["text"])

    def test_baseline_script_reports_counts_and_the_corpus_hash(self):
        corpus, digest = baseline.load()
        result = baseline.measure(corpus)
        scored = sum(1 for c in corpus["cases"] if c["label"] != "ambiguous")
        self.assertEqual(result["false_negatives"]["of"] + result["false_positives"]["of"], scored)
        out = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "run_r8_reassurance_baseline.py")],
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out)["corpus_sha256"], digest)


class ProposedPhase1Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(cls.schema)
        cls.validator = jsonschema.Draft202012Validator(cls.schema)

    def test_schema_is_marked_inactive_and_phase2_is_blocked(self):
        self.assertEqual(self.schema["x-status"], "PROPOSED_INACTIVE")
        self.assertEqual(self.schema["x-phase2"]["status"], "BLOCKED")
        self.assertEqual(self.schema["x-fixed-clause"]["status"], "DRAFT_PENDING_MEDICAL_WORDING")
        for lang in ("pt-PT", "pt-BR", "en"):
            self.assertIsNone(self.schema["x-fixed-clause"][lang])

    def test_valid_document_passes_and_states_are_closed(self):
        self.validator.validate(valid_document())
        for state in ("observable", "not_observable", "uncertain", "not_assessable"):
            doc = valid_document()
            doc["observations"]["chromatic_alteration"] = (
                {"state": state, "uncertainty_causes": ["lighting_tint"]} if state == "uncertain" else {"state": state})
            self.validator.validate(doc)
        doc = valid_document()
        doc["observations"]["chromatic_alteration"] = {"state": "normal"}
        self.assertFalse(self.validator.is_valid(doc))

    def test_uncertain_requires_a_cause_and_free_text_is_rejected(self):
        doc = valid_document()
        doc["observations"]["necrotic_appearing_tissue"] = {"state": "uncertain"}
        self.assertFalse(self.validator.is_valid(doc))
        doc["observations"]["necrotic_appearing_tissue"] = {"state": "uncertain", "uncertainty_causes": []}
        self.assertFalse(self.validator.is_valid(doc))
        for extra in ({"impression": "Benign lesion."}, {"alarm_class": "high"}, {"clause_text": "free text"}):
            self.assertFalse(self.validator.is_valid(valid_document(**extra)), extra)

    def test_phase2_fields_and_missing_signs_are_rejected(self):
        doc = valid_document()
        doc["observations"]["risk_class"] = {"state": "observable"}
        self.assertFalse(self.validator.is_valid(doc))
        doc = valid_document()
        del doc["observations"]["visible_edge_separation"]
        self.assertFalse(self.validator.is_valid(doc))

    def test_five_states_and_not_applicable_needs_a_confirmed_absent_premise(self):
        signs = self.schema["properties"]["observations"]["properties"]
        self.assertEqual(len(signs), 5)
        for name, sign in signs.items():
            self.assertEqual(sign["properties"]["state"]["enum"],
                             ["observable", "not_observable", "uncertain", "not_assessable", "not_applicable"], name)
            doc = valid_document()
            doc["observations"][name] = {"state": "not_applicable", "premise_absent_confirmed": True}
            self.validator.validate(doc)
            for bad in ({"state": "not_applicable"},
                        {"state": "not_applicable", "premise_absent_confirmed": False},
                        {"state": "not_applicable", "premise_absent_confirmed": True, "uncertainty_causes": ["shadow"]},
                        {"state": "not_applicable", "premise_absent_confirmed": "yes"},
                        {"state": "observable", "premise_absent_confirmed": True},
                        {"state": "not_observable", "premise_absent_confirmed": False},
                        {"state": "not_assessable", "premise_absent_confirmed": True}):
                doc = valid_document()
                doc["observations"][name] = bad
                self.assertFalse(self.validator.is_valid(doc), (name, bad))

    def test_not_applicable_stays_inside_the_inactive_contract_and_phase2_stays_blocked(self):
        self.assertEqual(self.schema["x-not-applicable"]["status"], "PROPOSED_INACTIVE")
        self.assertEqual(self.schema["x-not-applicable"]["decision"], "DEC-CLIN-R8-03")
        self.assertEqual(self.schema["x-not-applicable"]["premise_definitions"], "PENDING_MEDICAL_WORDING")
        self.assertEqual(self.schema["x-not-applicable"]["source_of_confirmation"],
                         "CLINICIAN_OR_EXPLICIT_CLINICAL_DATA_NEVER_IMAGE_ONLY")
        self.assertIn("no se infiere solo de la imagen", self.schema["x-not-applicable"]["rule"])
        for sign in self.schema["properties"]["observations"]["properties"].values():
            self.assertIn("No se infiere solo de la imagen", sign["properties"]["premise_absent_confirmed"]["description"])
        self.assertEqual(self.schema["x-phase2"]["status"], "BLOCKED")
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            self.assertNotIn("premise_absent_confirmed", path.read_text(encoding="utf-8", errors="ignore"), str(path))

    def test_the_proposal_is_not_wired_into_the_product(self):
        needles = ("skin-wound-phase1-contract", "phase1-0.1-proposed", "phase1-0.2-proposed")
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in needles:
                self.assertNotIn(needle, text, str(path))


if __name__ == "__main__":
    unittest.main()
