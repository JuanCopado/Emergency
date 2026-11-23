"""R5-1 policy layer 7 (DEC-CLIN-R15-01): INACTIVE specification of four closed technical triggers. Nothing here abstains.

The contract only fixes what a future, medically approved abstention could say and on what evidence.
It must stay out of the product, admit no free text, protect the classic and document flows, never
admit RGB, EXIF, the filename, the absence of DICOM, an isolated extension, pixel statistics, a model
output or an unproven clinical suspicion as evidence, and carry no literal message text until the
approved wording is supplied.
"""
import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).parents[1]
SCHEMA = ROOT / "references" / "modality-abstention-layer7.contract.proposed.json"

T1, T2, T3, T4 = ("T7-01_UNDECLARED_MODALITY", "T7-02_UNKNOWN_CONTRACT",
                  "T7-03_CORRUPT_UNPROCESSABLE", "T7-04_FORMAT_CONTAINER_MISMATCH")


def doc(**changes):
    base = {"contract_version": "layer7-0.2-proposed", "flow": "modality_entry", "modality_declared": True,
            "declared_kind": "ecg", "decision": "none", "provenance": "deterministic_rule"}
    base.update(changes)
    return base


def abstain(trigger, message, sources, **changes):
    return doc(decision="abstain", trigger_id=trigger, message_id=message, send_allowed=False,
               evidence={"sources": sources}, **changes)


T01 = abstain(T1, "MSG_T7_01", ["declared_modality_absent"], modality_declared=False, declared_kind=None)
T02 = abstain(T2, "MSG_T7_02", ["declared_kind_not_in_contract_registry"], declared_kind="unknown_kind")
T03 = abstain(T3, "MSG_T7_03", ["container_parse_error"])
T04 = abstain(T4, "MSG_T7_04", ["container_signature", "declared_extension"])


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

    def with_changes(self, base, **changes):
        merged = dict(base)
        merged.update(changes)
        return merged

    def test_marked_inactive_off_behind_a_flag_with_the_decision_recorded(self):
        self.assertEqual(self.schema["x-status"], "PROPOSED_INACTIVE")
        self.assertEqual(self.schema["x-decision"], "DEC-CLIN-R15-01")
        flag = self.schema["x-feature-flag"]
        self.assertIs(flag["default"], False)
        self.assertEqual(flag["production"], "IGNORED")
        self.assertIs(flag["connected_to_product"], False)
        self.assertEqual(list(self.schema["x-triggers"]), [T1, T2, T3, T4])

    def test_the_message_texts_are_not_invented_until_the_approved_literals_arrive(self):
        self.assertEqual(self.schema["x-message-texts-status"], "PENDING_APPROVED_LITERAL_TEXTS")
        self.assertEqual(sorted(self.schema["x-message-texts"]), ["MSG_T7_01", "MSG_T7_02", "MSG_T7_03", "MSG_T7_04"])
        for texts in self.schema["x-message-texts"].values():
            self.assertEqual(texts, {"es": None, "pt": None, "en": None})

    def test_each_trigger_and_the_no_decision_case_have_their_own_shape(self):
        for valid in (doc(), T01, T02, T03, T04):
            self.ok(valid)
        self.bad(doc(trigger_id=T3), "no decision cannot carry a trigger")
        self.bad(doc(message_id="MSG_T7_03"))
        self.bad(doc(evidence={"sources": ["container_parse_error"]}))
        self.bad(doc(send_allowed=False))
        self.bad(doc(modality_declared=False, declared_kind=None), "in the modality entry no decision needs a declared modality")

    def test_an_abstention_is_complete_and_never_forces_the_submission(self):
        for missing in ("trigger_id", "message_id", "evidence", "send_allowed"):
            self.bad({k: v for k, v in T03.items() if k != missing}, missing)
        self.bad(self.with_changes(T03, send_allowed=True))
        self.bad(self.with_changes(T03, trigger_id="T7-05_NEW"))
        self.bad(self.with_changes(T03, message_id="MSG_T7_05"))

    def test_t7_01_undeclared_modality(self):
        for change in ({"modality_declared": True}, {"declared_kind": "ecg"}, {"message_id": "MSG_T7_02"},
                       {"flow": "classic_upload"}, {"flow": "document_legacy_bridge"},
                       {"evidence": {"sources": ["container_parse_error"]}},
                       {"evidence": {"sources": ["declared_modality_absent", "container_signature"]}}):
            self.bad(self.with_changes(T01, **change), change)

    def test_t7_02_unknown_contract(self):
        for change in ({"modality_declared": False}, {"declared_kind": None}, {"message_id": "MSG_T7_01"},
                       {"flow": "classic_upload"}, {"flow": "document_legacy_bridge"},
                       {"evidence": {"sources": ["declared_modality_absent"]}}):
            self.bad(self.with_changes(T02, **change), change)

    def test_the_classic_and_document_flows_never_get_new_blocks_from_t7_01_or_t7_02(self):
        for flow in ("classic_upload", "document_legacy_bridge"):
            self.ok(doc(flow=flow, modality_declared=False, declared_kind=None))   # nothing is blocked
            self.bad(self.with_changes(T01, flow=flow))
            self.bad(self.with_changes(T02, flow=flow))
            for technical in (T03, T04):
                self.ok(self.with_changes(technical, flow=flow, modality_declared=False, declared_kind=None)
                        if flow == "document_legacy_bridge" else self.with_changes(technical, flow=flow))

    def test_the_document_legacy_bridge_carries_no_kind(self):
        self.ok(doc(flow="document_legacy_bridge", modality_declared=False, declared_kind=None))
        self.bad(doc(flow="document_legacy_bridge", modality_declared=True, declared_kind="pdf_document"))
        self.bad(doc(flow="document_legacy_bridge", declared_kind="ecg"))

    def test_t7_03_corrupt_or_unprocessable_needs_a_container_parse_error(self):
        for change in ({"message_id": "MSG_T7_04"}, {"evidence": {"sources": ["container_signature"]}},
                       {"evidence": {"sources": ["container_parse_error", "container_signature"]}}):
            self.bad(self.with_changes(T03, **change), change)

    def test_t7_04_needs_the_signature_paired_with_a_declared_format_and_never_an_extension_alone(self):
        self.ok(abstain(T4, "MSG_T7_04", ["container_signature", "declared_mime_type"]))
        self.ok(abstain(T4, "MSG_T7_04", ["container_signature", "declared_extension", "declared_mime_type"]))
        for sources in (["declared_extension"], ["declared_mime_type"], ["declared_extension", "declared_mime_type"],
                        ["container_signature"], ["container_signature", "container_parse_error"]):
            self.bad(abstain(T4, "MSG_T7_04", sources), sources)
        self.bad(self.with_changes(T04, message_id="MSG_T7_03"))

    def test_forbidden_evidence_is_never_accepted(self):
        forbidden = self.schema["x-forbidden-evidence"]
        self.assertEqual(set(forbidden), {"rgb", "exif", "filename", "dicom_absence", "isolated_extension",
                                          "pixel_statistics", "model_output", "unproven_clinical_suspicion"})
        allowed = set(self.schema["properties"]["evidence"]["properties"]["sources"]["items"]["enum"])
        self.assertEqual(allowed & set(forbidden), set())
        for source in forbidden:
            for base in (T01, T02, T03, T04):
                self.bad(self.with_changes(base, evidence={"sources": list(base["evidence"]["sources"]) + [source]}), source)
            self.bad(self.with_changes(T03, evidence={"sources": [source]}), source)

    def test_a_technically_valid_rgb_image_without_dicom_is_never_rejected_by_this_contract(self):
        # RGB and the absence of DICOM are not evidence sources, so a photograph of an ECG, radiograph or ultrasound
        # screen can only reach `decision: none`; any abstention that cites them is invalid.
        for kind in ("ecg", "xray", "pocus"):
            self.ok(doc(declared_kind=kind))
            for source in ("rgb", "dicom_absence"):
                self.bad(self.with_changes(T03, declared_kind=kind, evidence={"sources": [source]}), (kind, source))

    def test_no_free_text_no_model_provenance_and_no_clinical_classification(self):
        for extra in ({"message": "Imagen no compatible"}, {"impression": "x"}, {"content_class": "skin"},
                      {"confidence": 0.9}, {"model_output": "ecg"}, {"clinical_suspicion": "lesion"}):
            self.bad(self.with_changes(T03, **extra), extra)
        self.bad(self.with_changes(T03, provenance="model"))
        self.bad(self.with_changes(T03, provenance="classifier"))

    def test_the_contract_is_not_wired_into_the_product(self):
        needles = ("modality-abstention-layer7", "layer7-0.1-proposed", "layer7-0.2-proposed", "VITE_R51_LAYER7",
                   "T7-01_UNDECLARED_MODALITY", "MSG_T7_0")
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in needles:
                self.assertNotIn(needle, text, str(path))


if __name__ == "__main__":
    unittest.main()
