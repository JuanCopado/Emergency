"""R25 · stimulus bank: generated vs pending, metadata audit, perceptual separation, no adjudication claimed. Laboratory only."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import bank_r23 as bank  # noqa: E402

M = json.loads(bank.MANIFEST_PATH.read_text(encoding="utf-8"))


class Bank(unittest.TestCase):
    def test_counts_and_status(self):
        c = bank.status_counts(M)
        self.assertEqual((c["total"], c["generated_technical"], c["pending_stimulus_generation"], c["adjudicated"]), (30, 10, 20, 0))
        self.assertEqual(M["bank_status"], "NOT_FROZEN_NOT_VALIDATED")
        self.assertFalse((bank.HERE / "bank" / "HF_ETAPA1_STIMULI_SHA256.txt").exists())

    def test_nothing_is_adjudicated_or_visually_approved(self):
        for s in M["stimuli"]:
            self.assertEqual(s["clinical_adjudication_status"], "PENDING_CLINICAL_ADJUDICATION")
            self.assertEqual(s["clinical_adjudicator_signoff"], "PENDING")
            self.assertIn(s["visual_review_status"], {"PENDING_VISUAL_REVIEW", "NOT_APPLICABLE_NOT_GENERATED"})

    def test_pending_stimuli_state_their_impediment_and_have_no_file(self):
        pending = [s for s in M["stimuli"] if s["generation_status"] == bank.PENDING]
        self.assertEqual(len(pending), 20)
        for s in pending:
            self.assertIsNone(s["file"]); self.assertIsNone(s["sha256"]); self.assertIsNone(s["image_format"])
            self.assertTrue(s["generation_impediment"], s["stimulus_id"])
        self.assertEqual({s["true_modality"] for s in pending}, {"skin_wound", "xray", "pocus"})

    def test_generated_have_format_dimensions_provenance_and_clean_metadata(self):
        generated = [s for s in M["stimuli"] if s["file"]]
        self.assertEqual(len(generated), 10)
        for s in generated:
            self.assertTrue(s["image_format"]); self.assertEqual(s["metadata_findings"], [])
            self.assertIn("CC0", s["license_ref"]); self.assertTrue(s["origin_type"].startswith("synthetic_procedural"))
            if s["image_format"] != "PDF" and s["phash_64"]:
                self.assertTrue(s["width"] and s["height"])
        schematic = {s["stimulus_id"] for s in generated if s["origin_type"] == "synthetic_procedural_schematic"}
        self.assertEqual(schematic, bank.PROCEDURAL_SCHEMATIC)

    def test_bank_verifies_and_sets_are_perceptually_separated(self):
        self.assertEqual(bank.verify_bank(M), [])
        check = bank.interset_check(M)
        self.assertEqual(check["perceptually_too_close"], [])
        self.assertFalse(check["duplicate_sha256"])

    def test_metadata_audit_detects_identifying_containers(self):
        from PIL import Image
        import io
        img = Image.new("RGB", (8, 8), (10, 20, 30))
        buf = io.BytesIO(); img.save(buf, "JPEG", exif=b"Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00")
        self.assertIn("exif_or_xmp_app1", bank.audit_metadata(buf.getvalue()))
        buf = io.BytesIO(); img.save(buf, "PNG")
        self.assertEqual(bank.audit_metadata(buf.getvalue()), [])
        self.assertIn("pdf_author", bank.audit_metadata(b"%PDF-1.4\n/Author (Dr X)\n"))

    def test_metadata_finding_fails_verification(self):
        broken = json.loads(json.dumps(M))
        next(s for s in broken["stimuli"] if s["file"])["metadata_findings"] = ["exif_or_xmp_app1"]
        self.assertTrue(any("identifying metadata" in p for p in bank.verify_bank(broken)))

    def test_qa_cases_stay_outside_the_30(self):
        self.assertEqual(len(M["qa_technical"]), 2)
        self.assertFalse({s["stimulus_id"] for s in M["qa_technical"]} & {s["stimulus_id"] for s in M["stimuli"]})

    def test_generated_pdfs_are_byte_reproducible(self):
        a, b = bank.generate_bytes(), bank.generate_bytes()
        for name in ("S1-13.pdf", "S2-14.pdf", "S2-15.pdf"):
            self.assertEqual(a[name], b[name])


if __name__ == "__main__":
    unittest.main()
