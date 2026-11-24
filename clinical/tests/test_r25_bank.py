"""R25 · stimulus bank: generated vs pending, metadata audit, perceptual separation, no adjudication claimed. Laboratory only."""
import io
import json
import shutil
import sys
import tempfile
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
        self.assertIn("pdf_producer", bank.audit_metadata(b"%PDF-1.4\n/Producer (Private workstation)\n"))

    def test_metadata_finding_fails_verification(self):
        broken = json.loads(json.dumps(M))
        next(s for s in broken["stimuli"] if s["file"])["metadata_findings"] = ["exif_or_xmp_app1"]
        self.assertTrue(any("identifying metadata" in p for p in bank.verify_bank(broken)))

    def test_perceptual_hash_must_match_decoded_image(self):
        manifest = json.loads(json.dumps(M))
        row = next(s for s in manifest["stimuli"] if s["stimulus_id"] == "S1-08")
        row["phash_64"] = None
        self.assertIn("S1-08: perceptual hash does not match the manifest", bank.verify_bank(manifest))

    def test_metadata_is_checked_even_when_manifest_and_sha_agree(self):
        from PIL import Image

        manifest = json.loads(json.dumps(M))
        row = next(s for s in manifest["stimuli"] if s["stimulus_id"] == "S1-08")
        with tempfile.TemporaryDirectory() as temp:
            stimuli = Path(temp) / "stimuli"
            shutil.copytree(bank.STIMULI_DIR, stimuli)
            changed = io.BytesIO()
            with Image.open(stimuli / "S1-08.jpg") as img:
                img.save(changed, "JPEG", exif=b"Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00")
            data = changed.getvalue()
            (stimuli / "S1-08.jpg").write_bytes(data)
            row.update(bytes=len(data), sha256=bank.sha256_bytes(data), phash_64=bank.dhash64(data))
            self.assertIn("S1-08: identifying metadata found ['exif_or_xmp_app1']", bank.verify_bank(manifest, stimuli))

    def test_duplicate_bytes_are_reported_with_stale_manifest_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            stimuli = Path(temp) / "stimuli"
            shutil.copytree(bank.STIMULI_DIR, stimuli)
            shutil.copyfile(stimuli / "S1-08.jpg", stimuli / "S2-08.jpg")
            problems = bank.verify_bank(M, stimuli)
        self.assertIn("duplicate SHA-256 among generated stimuli", problems)
        self.assertIn("S2-08: bytes do not match the manifest", problems)

    def test_qa_cases_stay_outside_the_30(self):
        self.assertEqual(len(M["qa_technical"]), 2)
        self.assertFalse({s["stimulus_id"] for s in M["qa_technical"]} & {s["stimulus_id"] for s in M["stimuli"]})

    def test_generated_pdfs_are_byte_reproducible(self):
        a, b = bank.generate_bytes(), bank.generate_bytes()
        for name in ("S1-13.pdf", "S2-14.pdf", "S2-15.pdf"):
            self.assertEqual(a[name], b[name])
            self.assertEqual(a[name], (bank.STIMULI_DIR / name).read_bytes())


class GeminiCriteria(unittest.TestCase):
    def test_composition_per_set_matches_the_protocol(self):
        self.assertEqual(bank.composition_audit(M), [])
        broken = json.loads(json.dumps(M))
        next(s for s in broken["stimuli"] if s["mechanism_id"] == "M3")["mechanism_id"] = "M1"
        self.assertTrue(bank.composition_audit(broken))

    def test_lifecycle_states_are_separated_and_nothing_is_frozen(self):
        c = bank.status_counts(M)
        self.assertEqual(c["lifecycle"], {"GENERATED_NOT_ADJUDICATED": 10, "PENDING_STIMULUS_GENERATION": 20, "FROZEN": 0})
        for s in M["stimuli"]:
            self.assertFalse(s["review_controls"]["freeze_seal_eligible"])
            rc = s["review_controls"]["realism_review_360x640"]
            self.assertEqual((rc["reviewer_1"], rc["reviewer_2"], rc["third_adjudicator_if_disagreement"]), ("PENDING",) * 3)
            self.assertEqual(s["review_controls"]["visual_derivative_inspection"], "PENDING")

    def test_schematic_stimuli_are_not_assumed_valid(self):
        for s in M["stimuli"]:
            note = s["review_controls"]["validity_note"]
            if s["stimulus_id"] in bank.PROCEDURAL_SCHEMATIC:
                self.assertEqual(note, "NOT_ASSUMED_VALID_REQUIRES_REALISM_REVIEW")
            else:
                self.assertIsNone(note)

    def test_external_audit_report_records_what_was_and_was_not_run(self):
        report = json.loads((bank.HERE / "bank" / "external_audit_report.json").read_text(encoding="utf-8"))
        self.assertIn("exiftool", report["tools_found"])
        listed = {f["stimulus_id"] for f in report["files"]}
        self.assertEqual(listed, {s["stimulus_id"] for s in M["stimuli"] if s["file"]} | {q["stimulus_id"] for q in M["qa_technical"]})
        for f in report["files"]:
            if isinstance(f["pdfinfo"], dict):
                self.assertEqual(f["pdfinfo"]["identifying_fields_with_value"], [])
            if not report["tools_found"]["exiftool"]:
                self.assertEqual(f["exiftool"], "NOT_RUN_TOOL_UNAVAILABLE")
        self.assertIn("not a PHI review", report["scope"])


class Plausibility(unittest.TestCase):
    def test_ecg_rates_follow_the_stimulus_specification(self):
        rate = {s["stimulus_id"]: s["ecg_generator_parameters"]["heart_rate_bpm"] for s in M["stimuli"] if s["ecg_generator_parameters"]}
        self.assertEqual(set(rate), {"S1-08", "S2-08", "S1-09", "S2-09"})
        self.assertTrue(60 <= rate["S1-08"] <= 100, rate)       # sinus rhythm
        self.assertGreater(rate["S2-08"], 100)                  # sinus tachycardia (R25 sheet S2-08)
        for s in M["stimuli"]:
            if s["ecg_generator_parameters"]:
                self.assertFalse(s["ecg_generator_parameters"]["st_elevation"])
                self.assertEqual(s["ecg_generator_parameters"]["paper_speed_mm_s"], 25)

    def test_schematics_carry_a_justification_and_their_limits(self):
        for s in M["stimuli"]:
            rc = s["review_controls"]
            if s["stimulus_id"] in bank.PROCEDURAL_SCHEMATIC:
                self.assertIn("NOT assumed valid", rc["validity_justification"])
                self.assertTrue(rc["known_limitations"])
            else:
                self.assertIsNone(rc["validity_justification"])
        twelve = next(s for s in M["stimuli"] if s["stimulus_id"] == "S2-09")["review_controls"]["known_limitations"]
        self.assertIn("not clinically validated", twelve)

    def test_s2_09_limb_lead_identities_and_precordial_progression(self):
        leads = [bank.ecg_12_lead_sample(x / 200) for x in range(190)]
        expected_names = {name for row in bank.ECG_LEAD_LAYOUT for name in row}
        self.assertEqual(len(expected_names), 12)
        self.assertEqual(set(leads[0]), expected_names)
        for sample in leads:
            i, ii = sample["I"], sample["II"]
            self.assertAlmostEqual(sample["III"], ii - i)
            self.assertAlmostEqual(sample["aVR"], -(i + ii) / 2)
            self.assertAlmostEqual(sample["aVL"], i - ii / 2)
            self.assertAlmostEqual(sample["aVF"], ii - i / 2)
        self.assertEqual(len({tuple(sample[name] for sample in leads) for name in expected_names}), 12)
        r_wave = leads[64]
        s_wave = leads[70]
        self.assertLess(r_wave["V1"], r_wave["V2"])
        self.assertLess(r_wave["V2"], r_wave["V3"])
        self.assertLess(r_wave["V3"], r_wave["V4"])
        self.assertGreater(abs(s_wave["V1"]), r_wave["V1"])
        self.assertLess(abs(s_wave["V5"]), r_wave["V5"])
        for name in expected_names:
            self.assertAlmostEqual(leads[86][name], 0, delta=0.02)

    def test_mobile_scale_is_recorded_for_images_only(self):
        for s in M["stimuli"]:
            if s["file"] and s["image_format"] == "PDF":
                self.assertIsNone(s["mobile_360x640_contain_scale"])
            elif s["file"] and s["phash_64"]:
                self.assertTrue(0 < s["mobile_360x640_contain_scale"] <= 1.0)
            if s["stimulus_id"] == "S2-13":
                self.assertGreaterEqual(s["mobile_360x640_contain_scale"], 0.4)   # the printed text must survive the reduction


if __name__ == "__main__":
    unittest.main()
