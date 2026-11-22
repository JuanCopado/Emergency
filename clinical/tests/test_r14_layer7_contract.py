"""R14 · R5-1 policy layer 7: inactive proposed contract for neutral abstention. Nothing here abstains.

The contract only fixes what a future, medically approved abstention could say and on what evidence.
It must stay out of the product, admit no free text, and never admit RGB, EXIF, the filename, the
absence of DICOM, pixel statistics or a model output as evidence of the modality.
"""
import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).parents[1]
SCHEMA = ROOT / "references" / "modality-abstention-layer7.contract.proposed.json"


def doc(**changes):
    base = {"contract_version": "layer7-0.1-proposed", "modality_declared": True, "declared_kind": "ecg",
            "decision": "none", "provenance": "deterministic_rule"}
    base.update(changes)
    return base


UNDECLARED = doc(modality_declared=False, declared_kind=None, decision="abstain_modality_not_declared",
                 neutral_message_id="modality_not_declared")
INCOMPATIBLE = doc(decision="abstain_technical_incompatibility", neutral_message_id="technical_incompatibility",
                   incompatibility={"code": "declared_container_signature_mismatch",
                                    "evidence": {"sources": ["container_signature", "declared_extension"]}})


class Layer7Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(cls.schema)
        cls.validator = jsonschema.Draft202012Validator(cls.schema)

    def ok(self, document):
        self.validator.validate(document)

    def bad(self, document, why=""):
        self.assertFalse(self.validator.is_valid(document), why or document)

    def test_marked_inactive_with_pending_definitions(self):
        self.assertEqual(self.schema["x-status"], "PROPOSED_INACTIVE")
        self.assertEqual(self.schema["x-codes-status"], "PENDING_MEDICAL_DEFINITION")
        self.assertEqual(self.schema["x-message-wording"], "PENDING_MEDICAL_WORDING")

    def test_the_three_decisions_have_their_own_shape(self):
        self.ok(doc())
        self.ok(UNDECLARED)
        self.ok(INCOMPATIBLE)

    def test_no_decision_cannot_carry_an_incompatibility_or_a_message_or_an_undeclared_modality(self):
        self.bad(doc(neutral_message_id="technical_incompatibility"))
        self.bad(doc(incompatibility=INCOMPATIBLE["incompatibility"]))
        self.bad(doc(modality_declared=False, declared_kind=None), "no decision without a declared modality")

    def test_undeclared_modality_requires_no_declared_kind_and_the_neutral_message(self):
        self.bad({k: v for k, v in UNDECLARED.items() if k != "neutral_message_id"})
        self.bad(dict(UNDECLARED, modality_declared=True))
        self.bad(dict(UNDECLARED, declared_kind="ecg"))
        self.bad(dict(UNDECLARED, neutral_message_id="technical_incompatibility"))
        self.bad(dict(UNDECLARED, incompatibility=INCOMPATIBLE["incompatibility"]))

    def test_technical_incompatibility_needs_a_code_evidence_and_the_matching_message(self):
        self.bad({k: v for k, v in INCOMPATIBLE.items() if k != "incompatibility"})
        self.bad({k: v for k, v in INCOMPATIBLE.items() if k != "neutral_message_id"})
        self.bad(dict(INCOMPATIBLE, neutral_message_id="modality_not_declared"))
        self.bad(dict(INCOMPATIBLE, modality_declared=False))
        self.bad(dict(INCOMPATIBLE, incompatibility={"code": "declared_container_signature_mismatch", "evidence": {"sources": []}}))
        self.bad(dict(INCOMPATIBLE, incompatibility={"code": "looks_like_skin", "evidence": {"sources": ["container_signature"]}}))

    def test_forbidden_evidence_is_never_accepted(self):
        for source in self.schema["x-forbidden-evidence"]:
            with self.subTest(source=source):
                self.bad(dict(INCOMPATIBLE, incompatibility={"code": "declared_container_signature_mismatch",
                                                             "evidence": {"sources": [source]}}))
        allowed = set(self.schema["properties"]["incompatibility"]["properties"]["evidence"]["properties"]["sources"]["items"]["enum"])
        self.assertEqual(allowed & set(self.schema["x-forbidden-evidence"]), set())
        self.assertEqual(set(self.schema["x-forbidden-evidence"]),
                         {"rgb", "exif", "filename", "dicom_absence", "pixel_statistics", "model_output"})

    def test_no_free_text_no_model_provenance_and_no_content_classification(self):
        for extra in ({"message": "Imagen no compatible"}, {"impression": "x"}, {"content_class": "skin"},
                      {"confidence": 0.9}, {"model_output": "ecg"}):
            self.bad(dict(INCOMPATIBLE, **extra), extra)
        self.bad(dict(INCOMPATIBLE, provenance="model"))
        self.bad(dict(INCOMPATIBLE, provenance="classifier"))

    def test_the_contract_is_not_wired_into_the_product(self):
        needles = ("modality-abstention-layer7", "layer7-0.1-proposed")
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in needles:
                self.assertNotIn(needle, text, str(path))


if __name__ == "__main__":
    unittest.main()
