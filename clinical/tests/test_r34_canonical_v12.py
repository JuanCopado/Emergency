"""R34 · canonical-r27-v1.2 (successor contract): cryptographic integrity, manifest ground truth, provenance vocabulary, migration."""
import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "lab" / "human_factors"))
import canonical_r27_v1 as c1  # noqa: E402  (same module object the v1.2 module uses)
import canonical_r27_v12 as c  # noqa: E402
from canonical_r27_v1 import CanonicalViolation  # noqa: E402
from test_r31_outcomes_and_recovery import ctx, ev, selected  # noqa: E402


def locale_event(language="es", variant=None, status="OK", at=1):
    return ev("locale_resolved", at, language=language, lab_locale=variant, variant=variant, status=status)


UI_OF = {"ES": ("es", None), "EN": ("en", None), "pt-PT": ("pt", "pt-PT"), "pt-BR": ("pt", "pt-BR")}


class Bank:
    """Synthetic fixture bank: real files, real hashes, synthetic manifest (never the clinical bank)."""
    def __init__(self, truth):
        self.dir = tempfile.TemporaryDirectory()
        self.manifest = {}
        for stimulus_id, modality in truth.items():
            data = f"synthetic fixture {stimulus_id}".encode()
            (Path(self.dir.name) / f"{stimulus_id}.bin").write_bytes(data)
            self.manifest[stimulus_id] = {"stimulus_id": stimulus_id, "sha256": hashlib.sha256(data).hexdigest(), "file": f"stimuli/{stimulus_id}.bin",
                                          "true_modality": modality}

    def context(self, seq, period, pair, **over):
        context, width = ctx(seq, period, pair, **over)
        context["stimulus_hash_sha256"] = self.manifest[context["stimulus_id"]]["sha256"]
        context.pop("expected_modality", None)
        return context, width

    def v12(self, seq, period, pair, log, **over):
        context, width = self.context(seq, period, pair, **over)
        language, variant = UI_OF[context["language_stratum"]]
        return c.from_lab_ui_log_v12([locale_event(language, variant)] + log(width), context, self.manifest, self.dir.name)


M1_BYPASS = lambda w: [selected(w), ev("modality_selected", 20, modality="skin_wound", origin="initial"), ev("confirm_clicked", 900)]


class Integrity(unittest.TestCase):
    def setUp(self):
        self.bank = Bank({"S1-04": "ecg", "S1-08": None})
        self.addCleanup(self.bank.dir.cleanup)
        self.record = self.bank.v12("S1a", 1, 4, M1_BYPASS, data_provenance="SYNTHETIC_FIXTURE")

    def validate(self, record):
        return c.validate_record_v12(record, self.bank.manifest, self.bank.dir.name)

    def reject(self, **change):
        bad = {**self.record, **change}
        with self.assertRaises(CanonicalViolation):
            self.validate(bad)

    def test_positive_record_has_41_fields_and_a_verifiable_hash(self):
        self.assertEqual((len(self.record), self.record["schema_version"], self.record["expected_modality"], self.record["outcome_status"]),
                         (41, "canonical-r27-v1.2", "ecg", "bypass_residual"))
        self.assertEqual(self.record["payload_sha256"], hashlib.sha256(c.canonical_bytes(self.record)).hexdigest())
        self.validate(self.record)

    def test_payload_hash_false_absent_stale_and_resealed_tampering(self):
        self.reject(payload_sha256="0" * 64)                                                  # well-formed but false
        self.reject(payload_sha256="xyz")
        absent = dict(self.record)
        del absent["payload_sha256"]
        with self.assertRaises(CanonicalViolation):
            self.validate(absent)
        self.reject(participant_opaque_id="HF1-P999")                                        # modified after sealing: stale hash
        self.reject(**{"task_duration_ms": 1})
        tampered = c.seal({k: v for k, v in {**self.record, "task_duration_ms": 1}.items()})
        self.validate(tampered)                                                              # a re-sealed record is internally coherent (hash is integrity, not authorship)

    def test_serialization_is_deterministic_and_utf8(self):
        shuffled = dict(reversed(list(self.record.items())))
        self.assertEqual(c.canonical_bytes(self.record), c.canonical_bytes(shuffled))
        self.assertEqual(c.canonical_bytes({"a": "ñ", "b": 1}), b'{"a":"\xc3\xb1","b":1}')
        with self.assertRaises(CanonicalViolation):
            c.canonical_bytes({"x": float("nan")})

    def test_stimulus_hash_must_match_manifest_and_real_bytes(self):
        self.reject(stimulus_hash_sha256="f" * 64, payload_sha256=c.payload_hash({**self.record, "stimulus_hash_sha256": "f" * 64}))
        (Path(self.bank.dir.name) / "S1-04.bin").write_bytes(b"tampered bytes")
        with self.assertRaises(CanonicalViolation):
            self.validate(self.record)                                                       # file changed after the manifest was written
        (Path(self.bank.dir.name) / "S1-04.bin").unlink()
        with self.assertRaises(CanonicalViolation):
            self.validate(self.record)                                                       # file missing: not verifiable
        self.bank.manifest["S1-04"]["sha256"] = None
        with self.assertRaises(CanonicalViolation):
            self.validate(self.record)                                                       # bank not generated

    def test_expected_modality_is_manifest_only(self):
        context, width = self.bank.context("S1a", 1, 4, data_provenance="SYNTHETIC_FIXTURE")
        with self.assertRaises(CanonicalViolation):
            c.from_lab_ui_log_v12([locale_event()] + M1_BYPASS(width), {**context, "expected_modality": "ecg"}, self.bank.manifest, self.bank.dir.name)   # even if equal
        wrong = {**self.record, "expected_modality": "xray"}
        self.reject(expected_modality="xray", payload_sha256=c.payload_hash(wrong))

    def test_m1_conditional_rules_use_the_ground_truth(self):
        for outcome, declared in (("bypass_residual", "ecg"), ("detected_before_submit", "skin_wound"), ("valid_completed", "skin_wound")):
            changed = {**self.record, "outcome_status": outcome, "declared_modality": declared}
            changed["payload_sha256"] = c.payload_hash(changed)
            with self.assertRaises(CanonicalViolation):
                self.validate(changed)

    def test_unknown_stimulus_and_extra_fields_are_refused(self):
        self.reject(stimulus_id="S2-04", payload_sha256=c.payload_hash({**self.record, "stimulus_id": "S2-04"}))
        extra = {**self.record, "extra": 1}
        with self.assertRaises(CanonicalViolation):
            self.validate(extra)


class Provenance(unittest.TestCase):
    def setUp(self):
        self.bank = Bank({"S1-08": None})
        self.addCleanup(self.bank.dir.cleanup)
        self.log = lambda w: [selected(w), ev("confirm_clicked", 500)]

    def test_three_synthetic_values_are_accepted_and_preserved(self):
        for value in ("SYNTHETIC_FIXTURE", "SYNTHETIC_LAB_HARNESS", "TECHNICAL_DRY_RUN"):
            with self.subTest(value=value):
                self.assertEqual(self.bank.v12("S1a", 1, 8, self.log, data_provenance=value)["data_provenance"], value)

    def test_human_values_are_refused(self):
        for value in ("STAGE1_HUMAN_PILOT", "HUMAN_PARTICIPANT", "REAL", None):
            with self.subTest(value=value):
                with self.assertRaises(CanonicalViolation):
                    self.bank.v12("S1a", 1, 8, self.log, data_provenance=value)

    def test_stage1_is_still_refused_even_for_a_sealed_record(self):
        record = self.bank.v12("S1a", 1, 8, self.log, data_provenance="TECHNICAL_DRY_RUN")
        forged = c.seal({k: v for k, v in {**record, "data_provenance": "STAGE1_HUMAN_PILOT"}.items()})
        with self.assertRaises(CanonicalViolation):
            c.validate_record_v12(forged, self.bank.manifest, self.bank.dir.name)
        self.assertFalse(c.STAGE1_AUTHORIZED)


class Versions(unittest.TestCase):
    def setUp(self):
        self.bank = Bank({"S1-08": None})
        self.addCleanup(self.bank.dir.cleanup)
        context, width = ctx("S1a", 1, 8)
        context["stimulus_hash_sha256"] = self.bank.manifest["S1-08"]["sha256"]
        self.v11 = c1.from_lab_ui_log([selected(width), ev("confirm_clicked", 500)], context)

    def test_v11_and_v1_validators_are_intact_and_do_not_accept_v12(self):
        self.assertEqual(self.v11["data_provenance"], "SYNTHETIC_LAB_HARNESS")
        legacy = {**self.v11, "data_provenance": "HUMAN_PARTICIPANT"}
        c1.validate_record_v11(legacy)                                                       # historical v1.1 behaviour unchanged
        v12 = c.from_v11(self.v11, self.bank.manifest, self.bank.dir.name)
        with self.assertRaises(CanonicalViolation):
            c1.validate_record_v11(v12)
        with self.assertRaises(CanonicalViolation):
            c.validate_record_v12(self.v11, self.bank.manifest, self.bank.dir.name)
        with self.assertRaises(CanonicalViolation):
            c1.validate_record({k: v for k, v in v12.items()})

    def test_migration_is_deterministic_and_refuses_human_participant(self):
        a = c.from_v11(self.v11, self.bank.manifest, self.bank.dir.name)
        b = c.from_v11(copy.deepcopy(self.v11), self.bank.manifest, self.bank.dir.name)
        self.assertEqual(a, b)
        with self.assertRaises(CanonicalViolation):
            c.from_v11({**self.v11, "data_provenance": "HUMAN_PARTICIPANT"}, self.bank.manifest, self.bank.dir.name)


class RealReceptorManifest(unittest.TestCase):
    def test_only_stimuli_with_real_bytes_and_hash_are_exportable(self):
        manifest = c.load_manifest()
        for stimulus_id in ("S1-13", "S2-14"):
            c.verified_stimulus(stimulus_id, manifest)
        with self.assertRaises(CanonicalViolation):
            c.verified_stimulus("S1-04", manifest)                                           # no hash in the receptor bank: not generated

    def test_e1_with_a_real_technical_stimulus_exports_a_sealed_record(self):
        manifest = c.load_manifest()
        context, width = ctx("S1a", 2, 14, data_provenance="TECHNICAL_DRY_RUN")
        context["stimulus_hash_sha256"] = manifest[context["stimulus_id"]]["sha256"]
        context.pop("expected_modality", None)
        log = [locale_event(), ev("file_selected", 100, size=2048, with_modality=False, viewport_width_px=width, e1_entry=True),
               ev("layer7_banner_rendered", 150, trigger="T7-01_UNDECLARED_MODALITY", message_id="MSG_T7_A"),
               ev("modality_selected", 900, modality="ecg", origin="after_layer7"), ev("recovery_action", 901, action="change_modality"),
               ev("confirm_clicked", 2000)]
        record = c.from_lab_ui_log_v12(log, context)
        self.assertEqual((record["expected_modality"], record["e1_entry_mode"], record["data_provenance"]), (None, "ISOLATED_LAB_ENTRY_PR95", "TECHNICAL_DRY_RUN"))


class Locale(unittest.TestCase):
    def setUp(self):
        self.bank = Bank({"S1-08": None})
        self.addCleanup(self.bank.dir.cleanup)
        self.log = lambda w: [selected(w), ev("confirm_clicked", 500)]

    def export(self, stratum, events):
        context, width = self.bank.context("S1a", 1, 8, language_stratum=stratum, data_provenance="SYNTHETIC_FIXTURE")
        return c.from_lab_ui_log_v12(events + self.log(width), context, self.bank.manifest, self.bank.dir.name)

    def test_explicit_regional_portuguese_is_exported_with_its_proof(self):
        self.assertEqual(self.export("pt-PT", [locale_event("pt", "pt-PT")])["language_stratum"], "pt-PT")
        self.assertEqual(self.export("ES", [locale_event("es")])["language_stratum"], "ES")

    def test_no_event_generic_pt_unsupported_and_mismatched_locales_fail_hard(self):
        cases = [("pt-PT", []),                                                              # nothing proves the language
                 ("pt-PT", [locale_event("pt", None)]),                                      # generic pt is never upgraded
                 ("pt-BR", [locale_event("pt", "pt-BR", "UNSUPPORTED")]),                    # no approved pt-BR texts
                 ("pt-BR", [locale_event("pt", "pt-PT")]),                                   # variant disagrees with the stratum
                 ("pt-PT", [locale_event("pt", "pt-BR")]),
                 ("ES", [locale_event("en")]),                                               # UI language disagrees
                 ("ES", [locale_event("es", "pt-PT")]),                                      # non-Portuguese cannot carry a variant
                 ("pt", [locale_event("pt", "pt-PT")])]                                      # generic stratum from the harness
        for stratum, events in cases:
            with self.subTest(stratum=stratum, events=events):
                with self.assertRaises(CanonicalViolation):
                    self.export(stratum, events)


if __name__ == "__main__":
    unittest.main()
