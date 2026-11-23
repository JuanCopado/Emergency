"""R28 · canonical-r27-v1 contract: one positive and the mandatory rejections of Gemini table rows 1-9. Laboratory only."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
from human_factors import canonical_r27_v1 as c, alt_b, dryrun, bank_r23 as bank  # noqa: E402
from human_factors.canonical_r27_v1 import CanonicalViolation  # noqa: E402


def base_a():
    return {"participant_opaque_id": "P01", "role_group": "M", "language_stratum": "ES", "sequence": "AB", "period": 1,
            "arm": "A_real_react_control", "arm_a_implementation_mode": "real_react_r5_1_off", "arm_a_verified_real_react": True,
            "layer7_ui_enabled": False, "device_type": "mobile_narrow_360", "viewport_width_px": 360, "mechanism_id": "M3_valid_non_interference",
            "scenario_id": "A", "outcome_status": "valid_completed", "entry_flow": "legacy_circuit", "declared_modality": None,
            "selection_origin": "legacy_implicit", "transport_mode": "legacy_passthrough", "recovery_outcome": "NA", "recovery_action_type": None,
            "attempted_force_blocked": False, "layer7_execution_mode": "DISCONNECTED_LEGACY", "layer7_trigger_code": "NONE",
            "layer7_subreason_code": "NONE", "layer7_message_key": "NONE", "layer7_banner_rendered_ms": None, "schema_version": c.SCHEMA_VERSION}


def base_b_e1():
    r = base_a()
    r.update(arm="B_prototype_alt_b", arm_a_implementation_mode=None, arm_a_verified_real_react=False, layer7_ui_enabled=True,
             mechanism_id="M2_layer7_abstention", scenario_id="E1", outcome_status="technical_abstention_correct", entry_flow="explicit_prototype",
             declared_modality=None, selection_origin="none", transport_mode="typed_contract", recovery_outcome="recovered_correctly",
             layer7_execution_mode="SIMULATED_LAB_HARNESS_ONLY", layer7_trigger_code="T7-01",
             layer7_subreason_code="explicit_flow_missing_selection", layer7_message_key="MSG_T7_NO_MODALITY", layer7_banner_rendered_ms=120)
    return r


class Contract(unittest.TestCase):
    def reject(self, mutate, base=base_a):
        r = base()
        mutate(r)
        with self.assertRaises(CanonicalViolation):
            c.validate_record(r)

    def test_valid_records_pass(self):
        c.validate_record(base_a())
        c.validate_record(base_b_e1())

    def test_row1_role(self):
        for bad in ("clinician", None, "other", ""):
            self.reject(lambda r, b=bad: r.update(role_group=b))

    def test_row2_arm(self):
        self.reject(lambda r: r.update(arm_a_implementation_mode="mock"))
        self.reject(lambda r: r.update(layer7_ui_enabled=False), base_b_e1)
        self.reject(lambda r: r.update(layer7_execution_mode="DISCONNECTED_LEGACY"), base_b_e1)

    def test_row3_device(self):
        self.assertEqual([c.device_for_width(w) for w in (360, 390, 1280)], ["mobile_narrow_360", "mobile_narrow_390", "desktop_web"])
        for bad in (415, 800, None, 0):
            with self.assertRaises(CanonicalViolation):
                c.device_for_width(bad)
        self.reject(lambda r: r.update(device_type="desktop_web"))

    def test_row4_mechanism_scenario(self):
        for scenario, mech in c.SCENARIO_MECHANISM.items():
            r = base_a()
            r.update(scenario_id=scenario, mechanism_id=mech, outcome_status="valid_completed" if mech.startswith("M3") else "protocol_deviation")
            if mech.startswith("M2"):
                continue                                                    # M2 needs arm B; covered below
            c.validate_record(r)
        self.reject(lambda r: r.update(mechanism_id="M1_bypass_selection"), base_b_e1)

    def test_row5_language(self):
        self.assertEqual({c.LANGUAGE[k] for k in ("es-ES", "pt-PT", "pt-BR", "en")}, {"ES", "pt-PT", "pt-BR", "EN"})
        self.assertNotIn("pt", c.LANGUAGE)
        self.reject(lambda r: r.update(language_stratum="pt"))

    def test_row6_outcomes(self):
        self.reject(lambda r: r.update(outcome_status="aborted"))
        self.reject(lambda r: r.update(outcome_status="bypass_residual"))                         # bypass states only in M1
        self.reject(lambda r: r.update(outcome_status="technical_abstention_correct"))            # only M2 arm B
        self.reject(lambda r: r.update(layer7_trigger_code="T7-04"), base_b_e1)                   # without its subreason

    def test_row7_document_bridge_and_e1(self):
        r = base_b_e1()
        r.update(scenario_id="F", mechanism_id="M3_valid_non_interference", outcome_status="valid_completed", declared_modality="document",
                 selection_origin="explicit_user_selection", transport_mode="document_legacy_bridge", recovery_outcome="NA",
                 layer7_trigger_code="NONE", layer7_subreason_code="NONE", layer7_message_key="NONE", layer7_banner_rendered_ms=None)
        c.validate_record(r)                                                                       # kind=null chosen: PASS, no T7-01
        r2 = copy.deepcopy(r)
        r2.update(layer7_trigger_code="T7-01", layer7_subreason_code="explicit_flow_missing_selection", layer7_message_key="MSG_T7_NO_MODALITY")
        with self.assertRaises(CanonicalViolation):
            c.validate_record(r2)
        c.validate_record(base_b_e1())                                                             # E1: null + none -> T7-01
        self.reject(lambda x: x.update(selection_origin="legacy_implicit"), base_b_e1)

    def test_row8_recovery(self):
        self.reject(lambda r: r.update(recovery_outcome="NA"), base_b_e1)
        self.reject(lambda r: r.update(recovery_outcome="abandoned"))                              # M3 cannot carry recovery
        self.reject(lambda r: r.update(recovery_outcome="attempted_force_blocked"), base_b_e1)     # flag must agree

    def test_row9_layer7(self):
        self.assertEqual(len(c.L7_MAP), 5)
        self.reject(lambda r: r.update(layer7_trigger_code="T7-01", layer7_subreason_code="explicit_flow_missing_selection",
                                       layer7_message_key="MSG_T7_NO_MODALITY"))                   # trigger in arm A
        self.reject(lambda r: r.update(layer7_message_key="MSG_T7_CORRUPT_FILE"), base_b_e1)       # wrong text for the trigger

    def test_closed_fields(self):
        r = base_a()
        r["extra"] = 1
        with self.assertRaises(CanonicalViolation):
            c.validate_record(r)


class Adapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records, _ = dryrun.run(bank.build_manifest(), count=2)
        cls.rec = next(r for r in records if r["arm"] == "A" and r["scenario_code"] == "A")

    capture = {"arm_a_implementation_mode": "real_react_r5_1_off", "layer7_ui_enabled": False, "viewport_width_px": 360,
               "outcome_status": "valid_completed", "entry_flow": "legacy_circuit", "declared_modality": None,
               "selection_origin": "legacy_implicit", "transport_mode": "legacy_passthrough", "recovery_outcome": "NA",
               "attempted_force_blocked": False, "layer7_message_key": "NONE"}

    def test_conversion_requires_every_missing_field_and_never_defaults(self):
        before = copy.deepcopy(self.rec)
        out = c.from_alt_b_01(self.rec, dict(self.capture))
        self.assertEqual(out["schema_version"], c.SCHEMA_VERSION)
        self.assertEqual(self.rec, before)                                                          # source untouched
        for key in self.capture:
            partial = {k: v for k, v in self.capture.items() if k != key}
            with self.assertRaises(CanonicalViolation, msg=key):
                c.from_alt_b_01(self.rec, partial)

    def test_mock_source_and_missing_viewport_are_rejected(self):
        with self.assertRaises(CanonicalViolation):
            c.from_alt_b_01(self.rec, dict(self.capture, arm_a_implementation_mode="mock"))
        with self.assertRaises(CanonicalViolation):
            c.from_alt_b_01(self.rec, dict(self.capture, viewport_width_px=None))


if __name__ == "__main__":
    unittest.main()
