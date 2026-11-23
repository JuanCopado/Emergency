"""R24 · Alternative B laboratory: telemetry records, M1/M2/M3 separation, versioned export, stimulus bank, file probe and technical dry-run."""
import copy
import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "lab"))
import human_factors_tools as hf  # noqa: E402
from human_factors import alt_b, bank_r23 as bank, dryrun, file_probe  # noqa: E402

B = 60
MANIFEST = bank.build_manifest()
RECORDS, SOURCES = dryrun.run(MANIFEST, count=4, seed="t")


def export(records=None, manifest=None, resamples=B):
    return alt_b.export_alt_b(records or RECORDS, manifest or MANIFEST, resamples, "t", "abcdef1")


class Records(unittest.TestCase):
    def test_the_dry_run_records_validate_and_carry_the_required_telemetry(self):
        self.assertEqual(alt_b.validate_records(RECORDS, MANIFEST), 120)
        for field in ("participant_opaque_id", "role_group", "language_stratum", "sequence", "period", "arm", "device_type", "mechanism_id",
                      "scenario_id", "stimulus_hash_sha256", "declared_envelope", "preview_shown_ms", "modality_changed_after_preview",
                      "confirmation_clicked", "layer7_execution_mode", "layer7_trigger_code", "layer7_subreason_code", "recovery_outcome",
                      "outcome_status", "task_duration_ms"):
            self.assertIn(field, RECORDS[0])

    def test_unknown_missing_and_forbidden_fields_are_rejected(self):
        bad = copy.deepcopy(RECORDS)
        bad[0]["extra"] = 1
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)
        bad = copy.deepcopy(RECORDS)
        del bad[0]["task_duration_ms"]
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)
        for field in ("participant_name", "timestamp", "ip_address", "email", "verdict"):
            bad = copy.deepcopy(RECORDS)
            bad[0][field] = "x"
            with self.assertRaises(ValueError):
                alt_b.validate_records(bad, MANIFEST)

    def test_mechanism_must_match_the_scenario_code_and_the_manifest(self):
        for code, mechanism in alt_b.SCENARIO_MECHANISM.items():
            wrong = next(m for m in alt_b.MECHANISMS if m != mechanism)
            bad = copy.deepcopy(RECORDS)
            row = next(r for r in bad if r["scenario_code"] == code)
            row["mechanism_id"] = wrong
            with self.assertRaises(ValueError, msg=code):
                alt_b.validate_records(bad, MANIFEST)

    def test_stimulus_hash_must_match_the_manifest(self):
        bad = copy.deepcopy(RECORDS)
        row = next(r for r in bad if r["stimulus_hash_sha256"])
        row["stimulus_hash_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)
        bad = copy.deepcopy(RECORDS)
        row = next(r for r in bad if r["stimulus_hash_sha256"] is None)
        row["stimulus_hash_sha256"] = "1" * 64          # a pending stimulus cannot have a hash
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)

    def test_simulation_labels_per_arm(self):
        arm_a = next(r for r in RECORDS if r["arm"] == "A")
        arm_b = next(r for r in RECORDS if r["arm"] == "B")
        self.assertEqual(arm_a["layer7_execution_mode"], "NOT_APPLICABLE_ARM_A")
        self.assertEqual(arm_b["layer7_execution_mode"], "SIMULATED_LAB_HARNESS_ONLY")
        bad = copy.deepcopy(RECORDS)
        next(r for r in bad if r["arm"] == "A")["layer7_execution_mode"] = "SIMULATED_LAB_HARNESS_ONLY"
        with self.assertRaises(ValueError):                # arm A has no Layer 7: it cannot be credited with a harness
            alt_b.validate_records(bad, MANIFEST)
        bad = copy.deepcopy(RECORDS)
        next(r for r in bad if r["arm"] == "B")["layer7_execution_mode"] = "PRODUCTION"
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)
        bad = copy.deepcopy(RECORDS)
        row = next(r for r in bad if r["arm"] == "A")
        row["layer7_trigger_code"] = "T7-01_UNDECLARED_MODALITY"
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)

    def test_an_abstention_can_never_end_in_a_completed_send(self):
        bad = copy.deepcopy(RECORDS)
        row = next(r for r in bad if r["layer7_trigger_code"])
        row["confirmation_clicked"], row["outcome_status"] = True, "completed"
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)

    def test_sequence_period_and_arm_must_be_consistent(self):
        bad = copy.deepcopy(RECORDS)
        for r in bad:
            if r["participant_opaque_id"] == "DRY-01":
                r["sequence"] = "BA"                    # DRY-01 really is AB: period-1 arm A contradicts it
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)
        bad = copy.deepcopy(RECORDS)
        bad[0], bad[1] = dict(bad[0]), dict(bad[1])
        other = "B" if bad[0]["arm"] == "A" else "A"
        bad[1]["period"], bad[1]["arm"] = bad[0]["period"], other   # two arms in one period
        bad[1]["layer7_execution_mode"] = alt_b.HARNESS_MODE if other == "B" else alt_b.NOT_APPLICABLE_ARM_A
        with self.assertRaises(ValueError):
            alt_b.validate_records(bad, MANIFEST)


class Partition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = alt_b.summarize_alt_b(RECORDS, MANIFEST, B, "t")

    def test_counts_per_mechanism(self):
        self.assertEqual(self.out["mechanism_partition"], {"M1": 32, "M2": 16, "M3": 72})
        self.assertEqual(self.out["excluded_from_between_arm_contrasts"], ["M2"])

    def test_m2_is_one_arm_descriptive_and_has_no_between_arm_statistic(self):
        m2 = self.out["m2"]
        self.assertEqual(m2["between_arm_contrast"], "PROHIBITED_NOT_COMPUTED")
        self.assertIn("ONE ARM", m2["design"])
        text = json.dumps(m2)
        for banned in ("paired_difference", "mcnemar", "p_value", "cluster_bootstrap_95", "bca"):
            self.assertNotIn(banned, text)
        self.assertEqual(m2["arm_a_baseline_descriptive_only"]["layer7_triggers_recorded"], 0)

    def test_m2_records_are_never_converted_to_the_contrast_engine(self):
        row = next(r for r in RECORDS if r["mechanism_id"] == "M2")
        with self.assertRaises(ValueError):
            alt_b.to_legacy(row, MANIFEST)

    def test_changing_m2_records_does_not_change_the_m1_or_m3_contrasts(self):
        altered = copy.deepcopy(RECORDS)
        for r in altered:
            if r["mechanism_id"] == "M2":
                r["task_duration_ms"] += 9999
                r["comprehension_correct"] = False if r["arm"] == "B" else None
        again = alt_b.summarize_alt_b(altered, MANIFEST, B, "t")
        self.assertEqual(again["m1"], self.out["m1"])
        self.assertEqual(again["m3"], self.out["m3"])
        self.assertNotEqual(again["m2"], self.out["m2"])

    def test_removing_every_m2_record_leaves_m1_and_m3_untouched(self):
        without = [r for r in RECORDS if r["mechanism_id"] != "M2"]
        again = alt_b.summarize_alt_b(without, MANIFEST, B, "t")
        self.assertEqual(again["m1"], self.out["m1"])
        self.assertEqual(again["m3"], self.out["m3"])

    def test_small_cluster_flags_travel_with_every_mechanism(self):
        for key in ("m1", "m3"):
            self.assertTrue(self.out[key]["design"]["very_small_cluster_descriptive_only"])
            self.assertTrue(self.out[key]["design"]["small_cluster_warning"])
        self.assertTrue(self.out["m2"]["very_small_cluster_descriptive_only"])

    def test_layer7_firing_on_m1_and_m3_is_reported_with_the_dual_zero_event_rule(self):
        for key in ("m1", "m3"):
            fire = self.out[key]["layer7_firing_on_this_mechanism"]
            self.assertEqual(fire["layer7_fired"], 0)
            self.assertIn("never an exact trial-rate interval", fire["zero_event_report"]["label"])

    def test_an_unexpected_firing_is_surfaced_not_hidden(self):
        altered = copy.deepcopy(RECORDS)
        row = next(r for r in altered if r["mechanism_id"] == "M3" and r["arm"] == "B")
        row["layer7_trigger_code"], row["layer7_subreason_code"] = "T7-04_FORMAT_CONTAINER_MISMATCH", "modality_container_incompatible"
        row["confirmation_clicked"], row["outcome_status"] = False, "blocked_by_layer7"
        again = alt_b.summarize_alt_b(altered, MANIFEST, B, "t")
        self.assertEqual(again["m3"]["layer7_firing_on_this_mechanism"]["layer7_fired"], 1)


class Export(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = export()

    def test_labels_of_the_r23_protocol(self):
        d = self.doc
        self.assertEqual(d["study_stage"], "STAGE_1_FORMATIVE_ALT_B")
        self.assertEqual(d["layer7_execution_mode"], "SIMULATED_LAB_HARNESS_ONLY")
        self.assertEqual(d["study_status"], "NOT_EXECUTED_PROTOCOL_ONLY")
        self.assertEqual(d["tooling_status"], "NOT_EXECUTED_TOOLING_ONLY")
        self.assertEqual(d["layer7_result_label"], "SIMULATED_LAYER7_HARNESS_LAB_ONLY")
        self.assertEqual(d["unimplemented_stage2_models"], ["GLMM", "GEE_SMALL_SAMPLE", "DEVICE_ARM_INTERACTION"])
        self.assertEqual(d["acceptance_decision"], "PENDING_PHYSICIAN_OWNER_REVIEW")
        self.assertEqual(d["data_origin"], "SYNTHETIC_TECHNICAL_DRIVER")

    def test_each_label_keeps_its_own_meaning_and_historical_labels_are_not_replaced(self):
        self.assertNotEqual(alt_b.HARNESS_MODE, alt_b.LAYER7_RESULT_LABEL)
        self.assertNotEqual(alt_b.STUDY_STATUS, alt_b.TOOLING_STATUS)
        legacy = json.loads((ROOT / "references" / "human-factors-export.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(legacy["properties"]["study_stage"]["const"], "STAGE_1_FORMATIVE_ESTIMATION")
        self.assertEqual(legacy["properties"]["study_status"]["const"], "NOT_EXECUTED_TOOLING_ONLY")
        self.assertEqual(alt_b.LEGACY_STAGE, "STAGE_1_FORMATIVE_ESTIMATION")

    def test_valid_export_and_reproducibility(self):
        self.assertTrue(alt_b.validate_export(self.doc, RECORDS, MANIFEST))
        self.assertEqual(self.doc, export())
        self.assertNotEqual(self.doc["summary_sha256"], alt_b.export_alt_b(RECORDS, MANIFEST, B, "other", "abcdef1")["summary_sha256"])

    def test_versions_admitted_and_rejected(self):
        self.assertEqual(alt_b.SUPPORTED_VERSIONS, ("alt-b-0.1",))
        for version in ("alt-b-0.2", "alt-b-0.0", "stage1-0.1", "", None, 1):
            doc = dict(self.doc, schema_version=version)
            with self.assertRaises(ValueError, msg=str(version)):
                alt_b.validate_export(doc)
        legacy_like = {"study_stage": "STAGE_1_FORMATIVE_ESTIMATION", "study_status": "NOT_EXECUTED_TOOLING_ONLY"}
        with self.assertRaisesRegex(ValueError, "historical"):
            alt_b.validate_export(legacy_like)

    def test_the_historical_schema_rejects_an_alternative_b_export(self):
        import jsonschema
        legacy = json.loads((ROOT / "references" / "human-factors-export.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(list(jsonschema.Draft202012Validator(legacy).iter_errors(self.doc)))

    def test_required_fields_and_unknown_fields(self):
        for key in list(self.doc):
            doc = {k: v for k, v in self.doc.items() if k != key}
            with self.assertRaises(ValueError, msg=key):
                alt_b.validate_export(doc)
        with self.assertRaises(ValueError):
            alt_b.validate_export(dict(self.doc, surprise=True))

    def test_label_tampering_is_rejected(self):
        for key, value in (("study_stage", "STAGE_1_FORMATIVE_ESTIMATION"), ("layer7_execution_mode", "PRODUCTION"), ("study_status", "EXECUTED"),
                           ("data_origin", "HUMAN_PARTICIPANTS"), ("acceptance_decision", "APPROVED"), ("unimplemented_stage2_models", []),
                           ("layer7_result_label", "SIMULATED_LAB_HARNESS_ONLY")):
            with self.assertRaises(ValueError, msg=key):
                alt_b.validate_export(dict(self.doc, **{key: value}))

    def test_sha256_integrity(self):
        with self.assertRaises(ValueError):
            alt_b.validate_export(dict(self.doc, summary_sha256="0" * 64))
        with self.assertRaises(ValueError):
            alt_b.validate_export(dict(self.doc, records_sha256="0" * 64), RECORDS, MANIFEST)
        tampered = copy.deepcopy(RECORDS)
        tampered[0]["task_duration_ms"] += 1
        with self.assertRaises(ValueError):
            alt_b.validate_export(self.doc, tampered, MANIFEST)
        other = copy.deepcopy(MANIFEST)
        other["bank_status"] = "FROZEN"
        with self.assertRaises(ValueError):
            alt_b.validate_export(self.doc, RECORDS, other)
        altered_bytes = copy.deepcopy(MANIFEST)
        next(s for s in altered_bytes["stimuli"] if s["sha256"])["sha256"] = "2" * 64
        with self.assertRaises(ValueError):
            alt_b.validate_export(self.doc, RECORDS, altered_bytes)
        summary_tamper = copy.deepcopy(self.doc)
        summary_tamper["summary"]["m2"]["arm_b"]["trials"] = 999
        with self.assertRaises(ValueError):
            alt_b.validate_export(summary_tamper)

    def test_the_summary_cannot_carry_a_between_arm_m2_statistic(self):
        bad = copy.deepcopy(self.doc)
        bad["summary"]["m2"]["between_arm_contrast"] = "COMPUTED"
        with self.assertRaises(ValueError):
            alt_b.validate_export(bad)
        bad = copy.deepcopy(self.doc)
        bad["summary"]["excluded_from_between_arm_contrasts"] = []
        with self.assertRaises(ValueError):
            alt_b.validate_export(bad)

    def test_no_automatic_clinical_verdict_keys(self):
        self.assertEqual(alt_b.scan_export_for_verdicts(self.doc), [])
        bad = copy.deepcopy(self.doc)
        bad["summary"]["m1"]["clinical_conclusion"] = "safe"
        self.assertTrue(alt_b.scan_export_for_verdicts(bad))
        bad = copy.deepcopy(self.doc)
        bad["summary"]["m2"]["verdict"] = "pass"
        with self.assertRaises(ValueError):
            alt_b.validate_export(bad)

    def test_no_personal_data_dates_or_contact_details_in_records_or_export(self):
        text = json.dumps({"records": RECORDS, "export": self.doc})
        self.assertIsNone(re.search(r"[\w.]+@[\w.]+\.\w+", text))
        self.assertIsNone(re.search(r"\b\d{4}-\d{2}-\d{2}\b", text))              # no calendar dates
        self.assertIsNone(re.search(r"\b\d{3}[ .-]?\d{3}[ .-]?\d{3}\b", text))     # no phone-like numbers
        self.assertIsNone(re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text))         # no IP addresses
        self.assertFalse(any(re.search(r"time|date", k, re.I) and k not in ("task_duration_ms", "preview_shown_ms") for k in RECORDS[0]))

    def test_limitations_state_that_the_data_are_not_human(self):
        self.assertTrue(any("not from people" in x for x in self.doc["limitations"]))


class Bank(unittest.TestCase):
    def test_thirty_stimuli_two_sets_fifteen_pairs_each(self):
        self.assertEqual(len(MANIFEST["stimuli"]), 30)
        for set_id in (1, 2):
            rows = [s for s in MANIFEST["stimuli"] if s["set_id"] == set_id]
            self.assertEqual(sorted(s["pair_id"] for s in rows), list(range(1, 16)))
            counts = {m: sum(s["mechanism_id"] == m for s in rows) for m in ("M1", "M2", "M3")}
            self.assertEqual(counts, {"M1": 4, "M2": 2, "M3": 9})              # R23: 9 legitimate (60 %), 6 adversarial/technical (40 %)
        self.assertEqual({s["scenario_code"] for s in MANIFEST["stimuli"]}, set(alt_b.SCENARIO_MECHANISM))

    def test_the_bank_is_not_frozen_validated_or_adjudicated(self):
        self.assertEqual(MANIFEST["bank_status"], "NOT_FROZEN_NOT_VALIDATED")
        counts = bank.status_counts(MANIFEST)
        self.assertEqual((counts["generated_technical"], counts["pending_stimulus_generation"], counts["adjudicated"]), (5, 25, 0))
        for s in MANIFEST["stimuli"]:
            self.assertEqual(s["clinical_adjudicator_signoff"], "PENDING")
            self.assertIsNone(s["phi_audit_passed"])                            # human pixel/metadata review is still pending
            if s["generation_status"] == bank.PENDING:
                self.assertIsNone(s["sha256"]); self.assertIsNone(s["file"]); self.assertIsNone(s["license_ref"])
        self.assertFalse((bank.HERE / "bank" / "HF_ETAPA1_STIMULI_SHA256.txt").exists())   # the freeze seal must not exist yet

    def test_hashes_are_over_the_real_bytes_of_the_committed_files(self):
        self.assertEqual(bank.verify_bank(MANIFEST), [])
        for s in MANIFEST["stimuli"]:
            if s["file"]:
                data = (bank.HERE / "bank" / s["file"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), s["sha256"])
                self.assertEqual(len(data), s["bytes"])
        committed = json.loads(bank.MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(committed, MANIFEST)

    def test_tampering_with_a_file_or_the_manifest_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "stimuli").mkdir()
            for name, data in bank.generate_bytes().items():
                (root / "stimuli" / name).write_bytes(data)
            manifest = bank.build_manifest(root / "stimuli")
            self.assertEqual(bank.verify_bank(manifest, root / "stimuli"), [])
            (root / "stimuli" / "S2-14.pdf").write_bytes(b"%PDF-tampered")
            self.assertTrue(any("S2-14" in p for p in bank.verify_bank(manifest, root / "stimuli")))
            (root / "stimuli" / "S2-14.pdf").unlink()
            self.assertTrue(any("file missing" in p for p in bank.verify_bank(manifest, root / "stimuli")))
        broken = copy.deepcopy(MANIFEST)
        broken["stimuli"].pop()
        self.assertTrue(bank.verify_bank(broken))

    def test_duplicates_and_perceptual_similarity_are_detected(self):
        from PIL import Image
        import io
        def png(color, noise):
            img = Image.new("RGB", (64, 64), color)
            for i in range(64):
                img.putpixel((i, (i * noise) % 64), (255 - color[0], 0, 0))
            out = io.BytesIO(); img.save(out, "PNG"); return out.getvalue()
        a, near, far = png((200, 200, 200), 3), png((201, 200, 200), 3), png((10, 80, 160), 17)
        self.assertEqual(bank.hamming(bank.dhash64(a), bank.dhash64(near)) < bank.HAMMING_MIN, True)
        self.assertIsNone(bank.dhash64(b"%PDF-1.4 not an image"))
        def entry(sid, set_id, data):
            return {"stimulus_id": sid, "set_id": set_id, "phash_64": bank.dhash64(data), "sha256": bank.sha256_bytes(data)}
        close = bank.interset_check({"stimuli": [entry("S1-01", 1, a), entry("S2-01", 2, near)]})
        self.assertTrue(close["perceptually_too_close"])
        identical = bank.interset_check({"stimuli": [entry("S1-01", 1, a), entry("S2-01", 2, a)]})
        self.assertTrue(identical["duplicate_sha256"])
        clean = bank.interset_check({"stimuli": [entry("S1-01", 1, a), entry("S2-01", 2, far)]})
        self.assertEqual((clean["perceptually_too_close"], clean["duplicate_sha256"]), ([], False))

    def test_generated_files_are_clean_and_synthetic(self):
        for s in MANIFEST["stimuli"]:
            if s["file"]:
                self.assertEqual(s["origin_type"], "synthetic_procedural")
                self.assertTrue(s["license_ref"].startswith("CC0-1.0"))
        png = (bank.STIMULI_DIR / "S1-14.png").read_bytes()
        from PIL import Image
        import io
        self.assertEqual(dict(Image.open(io.BytesIO(png)).info).get("exif"), None)
        pdf = (bank.STIMULI_DIR / "S1-13.pdf").read_bytes().decode("latin-1")
        self.assertIn("NO CLINICO", pdf)
        self.assertNotRegex(pdf, r"/Author\s*\([^)]+\)")      # no author metadata

    def test_the_stimuli_specifications_follow_the_r23_table(self):
        by = {s["stimulus_id"]: s for s in MANIFEST["stimuli"]}
        self.assertEqual(by["S1-14"]["expected_layer7_trigger"], "T7-01_UNDECLARED_MODALITY")
        self.assertEqual(by["S1-15"]["expected_layer7_trigger"], "T7-03_CORRUPT_UNPROCESSABLE")
        self.assertEqual(by["S2-15"]["expected_layer7_trigger"], "T7-04_FORMAT_CONTAINER_MISMATCH")
        self.assertEqual({by[f"S1-{n:02d}"]["route_modality"] for n in (4, 5)}, {"ecg"})
        self.assertEqual(by["S1-06"]["route_modality"], "xray"); self.assertEqual(by["S1-07"]["route_modality"], "pocus")
        self.assertEqual((by["S1-01"]["mst_band"], by["S2-03"]["mst_band"], by["S2-06"]["mst_band"]), (2, 9, 8))
        for n in range(1, 16):
            if n not in (14, 15):
                self.assertIsNone(by[f"S1-{n:02d}"]["expected_layer7_trigger"])      # Layer 7 never fires on M1/M3 stimuli


class FileProbe(unittest.TestCase):
    def descriptor(self, name, flow, kind):
        return file_probe.describe(bank.STIMULI_DIR / name, flow, kind)

    def test_real_bytes_drive_the_four_trigger_families(self):
        from human_factors import layer7_harness as harness
        cases = [("S1-14.png", "modality_entry", None, "T7-01_UNDECLARED_MODALITY", "MSG_T7_A"),
                 ("S2-14.pdf", "modality_entry", None, "T7-01_UNDECLARED_MODALITY", "MSG_T7_A"),
                 ("S1-15.jpg", "modality_entry", "skin_wound", "T7-03_CORRUPT_UNPROCESSABLE", "MSG_T7_C"),
                 ("S2-15.pdf", "modality_entry", "skin_wound", "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_B"),
                 ("QA-01.wav", "modality_entry", "skin_wound", "T7-04_FORMAT_CONTAINER_MISMATCH", "MSG_T7_D"),
                 ("QA-02.jpg", "modality_entry", "skin_wound", "T7-03_CORRUPT_UNPROCESSABLE", "MSG_T7_C"),
                 ("S1-13.pdf", "document_legacy_bridge", None, None, None)]
        for name, flow, kind, trigger, message in cases:
            for language in harness.LANGUAGES:
                out = harness.run_case("B", self.descriptor(name, flow, kind), language)
                self.assertEqual((out["trigger_id"], out.get("message_id")), (trigger, message), name)
                if trigger:
                    self.assertFalse(out["send_allowed"])

    def test_the_truncated_jpeg_has_a_valid_signature_but_does_not_parse(self):
        d = self.descriptor("S1-15.jpg", "modality_entry", "skin_wound")
        self.assertEqual((d["signature_kind"], d["container_parse_ok"]), ("jpeg", False))

    def test_the_probe_never_looks_at_the_file_name_for_meaning(self):
        with tempfile.TemporaryDirectory() as tmp:
            decoy = Path(tmp) / "ecg_guardia_01.jpg"                        # name suggests ECG; bytes are a PDF
            decoy.write_bytes((bank.STIMULI_DIR / "S2-15.pdf").read_bytes())
            d = file_probe.describe(decoy, "modality_entry", "skin_wound")
            self.assertEqual(d["signature_kind"], "pdf")
            self.assertEqual(set(d), {"flow", "modality_declared", "declared_kind", "signature_kind", "container_parse_ok", "declared_mime_type", "declared_extension"})


class DryRun(unittest.TestCase):
    def test_thirty_tasks_per_participant_two_sets_two_arms(self):
        per = {}
        for r in RECORDS:
            per.setdefault(r["participant_opaque_id"], []).append(r)
        self.assertEqual(len(per), 4)
        for pid, rows in per.items():
            self.assertEqual(len(rows), 30)
            self.assertEqual({r["scenario_id"][:2] for r in rows if r["period"] == 1} | {r["scenario_id"][:2] for r in rows if r["period"] == 2}, {"S1", "S2"})
            for period in (1, 2):
                in_period = [r for r in rows if r["period"] == period]
                self.assertEqual(len(in_period), 15)
                self.assertEqual(len({r["scenario_id"][:2] for r in in_period}), 1)      # one disjoint set per period
                self.assertEqual(len({r["arm"] for r in in_period}), 1)
                self.assertEqual(sorted(r["trial_order"] for r in in_period), list(range(1, 16)))
            self.assertEqual({r["arm"] for r in rows}, {"A", "B"})
            self.assertEqual({r["device_type"] for r in rows}, {"mobile_narrow", "desktop_web"})

    def test_ab_ba_counterbalancing_and_set_counterbalancing(self):
        sequences = {r["participant_opaque_id"]: r["sequence"] for r in RECORDS}
        self.assertEqual(sorted(sequences.values()), ["AB", "AB", "BA", "BA"])
        first_set = {pid: next(r["scenario_id"][:2] for r in RECORDS if r["participant_opaque_id"] == pid and r["period"] == 1) for pid in sequences}
        self.assertEqual(sorted(first_set.values()), ["S1", "S1", "S2", "S2"])
        first_device = {pid: next(r["device_type"] for r in RECORDS if r["participant_opaque_id"] == pid and r["period"] == 1) for pid in sequences}
        self.assertEqual(len(set(first_device.values())), 2)

    def test_anti_priming_the_first_two_tasks_are_never_both_m1(self):
        for pid in {r["participant_opaque_id"] for r in RECORDS}:
            for period in (1, 2):
                first = sorted((r for r in RECORDS if r["participant_opaque_id"] == pid and r["period"] == period), key=lambda r: r["trial_order"])[:2]
                self.assertFalse(all(r["mechanism_id"] == "M1" for r in first))

    def test_the_driver_is_deterministic_and_has_no_arm_effect(self):
        again, _ = dryrun.run(MANIFEST, count=4, seed="t")
        self.assertEqual(again, RECORDS)
        other, _ = dryrun.run(MANIFEST, count=4, seed="u")
        self.assertNotEqual(other, RECORDS)
        # the scripted selection errors depend only on (participant, stimulus): the same set of M1 wrong selections is a pure function of that pair
        wrong = {(r["participant_opaque_id"], r["scenario_id"]) for r in RECORDS if r["mechanism_id"] == "M1" and r["initial_modality"] != "skin_wound"}
        expected = {(r["participant_opaque_id"], r["scenario_id"]) for r in RECORDS if r["mechanism_id"] == "M1" and dryrun._h(r["participant_opaque_id"], r["scenario_id"], "err") % 8 == 0}
        self.assertEqual(wrong, expected)

    def test_layer7_fires_only_on_m2_arm_b_and_only_as_the_manifest_expects(self):
        fired = [r for r in RECORDS if r["layer7_trigger_code"]]
        self.assertTrue(fired)
        for r in fired:
            self.assertEqual((r["mechanism_id"], r["arm"]), ("M2", "B"))
            self.assertEqual(r["layer7_trigger_code"], next(s for s in MANIFEST["stimuli"] if s["stimulus_id"] == r["scenario_id"])["expected_layer7_trigger"])
            self.assertFalse(r["confirmation_clicked"])
            self.assertEqual(r["outcome_status"], "blocked_by_layer7")
        self.assertFalse([r for r in RECORDS if r["mechanism_id"] in ("M1", "M3") and r["layer7_trigger_code"]])

    def test_descriptor_sources_are_declared_real_bytes_versus_spec_only(self):
        self.assertEqual(SOURCES, {"REAL_FILE_BYTES": 20, "SPEC_ONLY_NO_FILE": 100})

    def test_the_whole_pipeline_exports_validates_and_verifies_every_hash(self):
        out = dryrun.full_dry_run(resamples=B, count=4, seed="t")
        self.assertEqual(out["bank_problems"], [])
        self.assertEqual((out["records"], out["tasks_per_participant"]), (120, 30))
        self.assertTrue(alt_b.validate_export(out["export"], out["records_data"], out["manifest"]))
        self.assertEqual(out["export"]["study_status"], "NOT_EXECUTED_PROTOCOL_ONLY")


class Isolation(unittest.TestCase):
    NEEDLE = re.compile(r"alt_b|bank_r23|file_probe|dryrun|layer7_harness|human_factors|clinical/lab|VITE_R51_LAYER7")

    def test_product_sources_do_not_reference_the_new_lab_modules(self):
        offenders = []
        repo = ROOT.parent
        for base in ("app/src", "app/vite.config.ts", "app/package.json", "app/index.html", "app/public"):
            path = repo / base
            files = [path] if path.is_file() else list(path.rglob("*")) if path.exists() else []
            for f in files:
                if f.is_file() and f.suffix in {".ts", ".tsx", ".js", ".mjs", ".cjs", ".json", ".html", ".css"} and "generatedClinicalGuides" not in f.name:
                    if self.NEEDLE.search(f.read_text(encoding="utf-8", errors="ignore")):
                        offenders.append(str(f.relative_to(repo)))
        self.assertEqual(offenders, [])

    def test_stimulus_files_are_not_under_the_app_or_the_public_folder(self):
        repo = ROOT.parent
        for name in bank.generate_bytes():
            self.assertEqual(list((repo / "app").rglob(name)) if (repo / "app").exists() else [], [], name)

    def test_the_product_python_does_not_import_the_lab(self):
        import ast
        for f in (ROOT / "scripts").glob("*.py"):
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                for n in names:
                    self.assertFalse(re.match(r"(human_factors|alt_b|bank_r23|dryrun|file_probe|layer7_)", n), f"{f.name} imports {n}")

    def test_the_lab_modules_use_no_network_or_process_apis(self):
        import ast
        for module in ("alt_b.py", "bank_r23.py", "file_probe.py", "dryrun.py", "layer7_harness.py"):
            tree = ast.parse((ROOT / "lab" / "human_factors" / module).read_text(encoding="utf-8"))
            imports = {n.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for n in node.names}
            imports |= {(node.module or "").split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
            self.assertFalse(imports & {"socket", "urllib", "http", "requests", "subprocess", "shutil", "ftplib", "smtplib"}, (module, imports))

    def test_protected_flows_and_the_kind_null_bridge_are_untouched_by_layer7(self):
        from human_factors import layer7_harness as harness
        for flow in ("classic_upload", "document_legacy_bridge"):
            for signature in ("jpeg", "png", "pdf", "webp"):
                descriptor = {"flow": flow, "modality_declared": False, "declared_kind": None, "signature_kind": signature, "container_parse_ok": True,
                              "declared_mime_type": None, "declared_extension": None}
                self.assertIsNone(harness.run_case("B", descriptor, "es")["trigger_id"], (flow, signature))


if __name__ == "__main__":
    unittest.main()
