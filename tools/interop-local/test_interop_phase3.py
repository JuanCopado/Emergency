import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import interop_lab as lab
import interop_phase2 as phase2
import interop_phase3 as phase3


def bundle():
    return phase3.with_specimen(phase2.bundle_for_results([
        lab.synthetic_observation("718-7", 13.2), lab.synthetic_observation("2345-7", 100.0)]))


class StructuralExchangeTests(unittest.TestCase):
    def test_specimen_resources_linked_without_mutating_input(self):
        original = phase2.bundle_for_results([lab.synthetic_observation()])
        previous = copy.deepcopy(original)
        extended = phase3.with_specimen(original)
        self.assertEqual(original, previous)
        self.assertEqual(phase3.validate_bundle(extended), extended)
        resources = [entry["resource"] for entry in extended["entry"]]
        self.assertEqual([r["resourceType"] for r in resources],
                         ["Patient", "Specimen", "Observation", "DiagnosticReport"])
        self.assertEqual(resources[1], phase3.SPECIMEN)
        self.assertEqual(resources[2]["specimen"], phase3.SPECIMEN_REF)
        self.assertEqual(resources[3]["specimen"], [phase3.SPECIMEN_REF])

    def test_wrong_version_shape_count_or_contract_rejected(self):
        with self.assertRaises(lab.ContractError):phase3.validate_bundle(bundle(), "5.0.0")
        for value in [None, [], {"resourceType": "Bundle"}]:
            with self.assertRaises(lab.ContractError):phase3.validate_bundle(value)
        for mutate in [lambda b:b.update(id="other"),
                       lambda b:b["meta"].update(versionId="2"),
                       lambda b:b.update(entry=[]),
                       lambda b:b["entry"][1].update(resource=None)]:
            value = bundle();mutate(value)
            with self.assertRaises(lab.ContractError):phase3.validate_bundle(value)

    def test_specimen_real_fields_subject_and_external_references_rejected(self):
        for mutate in [lambda b:b["entry"][1]["resource"].update(identifier=[{"value":"person"}]),
                       lambda b:b["entry"][1]["resource"].update(subject={"reference":"Patient/other"}),
                       lambda b:b["entry"][2]["resource"].update(specimen={"reference":"https://invalid.example/1"}),
                       lambda b:b["entry"][-1]["resource"].update(specimen=[]),
                       lambda b:b["entry"][0]["resource"].update(active=0),
                       lambda b:b["entry"][2]["resource"]["valueQuantity"].update(unit="g/L")]:
            value = bundle();mutate(value)
            with self.assertRaises(lab.ContractError):phase3.validate_bundle(value)

    def test_fhir_parser_duplicate_keys_nonfinite_and_precision_rejected(self):
        raw = json.dumps(bundle()).encode("utf8")
        self.assertEqual(phase3.decode_fhir(raw), bundle())
        for invalid in [b"", b"{}"*(lab.MAX_MESSAGE+1), raw.replace(b'"value": 13.2', b'"value": 13.20'),
                        raw.replace(b'"value": 13.2', b'"value": NaN'),
                        raw.replace(b'"active": false', b'"active": false, "active": false')]:
            with self.subTest(size=len(invalid)):
                with self.assertRaises((lab.ContractError, ValueError)):phase3.decode_fhir(invalid)

    def test_single_oru_and_panel_preserve_values_units_codes_and_ack_identity(self):
        single = phase3.receive_hl7(lab.hl7_fixture().encode("ascii"))
        panel = phase3.receive_hl7(phase2.hl7_panel_fixture().encode("ascii"))
        self.assertIn("MSA|AA|SYNTHETIC-0001", single["ack"])
        self.assertIn("MSA|AA|SYNTHETIC-PHASE2-0001", panel["ack"])
        self.assertEqual(len(single["bundle"]["entry"]), 4)
        observations = panel["bundle"]["entry"][2:-1]
        values = {r["resource"]["code"]["coding"][0]["code"]:r["resource"]["valueQuantity"]
                  for r in observations}
        self.assertEqual(json.dumps(values["2345-7"]["value"]), "100.0")
        self.assertEqual(values["718-7"]["unit"], "g/dL")
        self.assertEqual(values["2345-7"]["unit"], "mg/dL")
        self.assertFalse(panel["unit_conversion"])
        self.assertEqual(phase3.validate_bundle(panel["bundle"]), panel["bundle"])

    def test_hl7_bad_precision_frame_version_code_and_units_rejected(self):
        raw = phase2.hl7_panel_fixture().encode("ascii")
        for invalid in [raw.replace(b"13.2", b"13.20"), raw.replace(b"g/dL", b"g/L"),
                        raw.replace(b"2.5.1", b"2.6"), raw.replace(b"718-7", b"unknown"),
                        raw.replace(b"\r", b"\n"), b"\x0b"+raw+b"\x1c\r", raw+b"PID|person\r"]:
            with self.assertRaises(lab.ContractError):phase3.receive_hl7(invalid)


class GatewaySecurityTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.gateway = phase3.SyntheticGateway(clock=lambda:self.now)
        self.token = self.gateway.issue_lab_credential("technician")

    def error(self, response, code):
        self.assertEqual(response, phase3.outcome(code))

    def test_crypto_credential_not_stored_in_clear_and_no_network(self):
        self.assertEqual(len(self.token), 64)
        self.assertNotIn(self.token, repr(self.gateway.__dict__))
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            response = self.gateway.exchange("hl7", self.token, lab.hl7_fixture().encode("ascii"))
            self.assertIn("bundle", response)
            self.assertTrue(self.gateway.exchange("pacs-store", self.token, lab.dicom_fixture())["stored"])

    def test_missing_wrong_foreign_and_unicode_credentials_rejected(self):
        other = phase3.SyntheticGateway().issue_lab_credential("technician")
        for token in [None, "", "x"*64, "é"*64, other, {}, self.token+"x"]:
            self.error(self.gateway.exchange("pacs-store", token, lab.dicom_fixture()), "forbidden")
        self.assertEqual(self.gateway.retention_status()["instances"], 0)

    def test_role_limit_cannot_store_and_unknown_role_lifetime_rejected(self):
        reviewer = self.gateway.issue_lab_credential("reviewer")
        self.error(self.gateway.exchange("pacs-store", reviewer, lab.dicom_fixture()), "forbidden")
        for role in ["admin", "", "hospital", None, []]:
            with self.assertRaises(lab.ContractError):self.gateway.issue_lab_credential(role)
        for seconds in [0, 121, True, 1.5]:
            with self.assertRaises(lab.ContractError):self.gateway.issue_lab_credential("reviewer", seconds=seconds)

    def test_rotate_revokes_prior_credential_and_payload(self):
        self.gateway.exchange("pacs-store", self.token, lab.dicom_fixture())
        new = self.gateway.issue_lab_credential("technician")
        self.error(self.gateway.exchange("pacs-read", self.token), "forbidden")
        self.error(self.gateway.exchange("pacs-read", new), "not-found")
        self.assertEqual(self.gateway.retention_status()["instances"], 0)

    def test_expiry_revokes_credential_and_clears_payload(self):
        token = self.gateway.issue_lab_credential("technician", seconds=1)
        self.gateway.exchange("pacs-store", token, lab.dicom_fixture())
        self.now += 1
        self.error(self.gateway.exchange("pacs-read", token), "expired")
        self.assertEqual(self.gateway.retention_status()["instances"], 0)
        self.assertFalse(self.gateway.retention_status()["session_active"])

    def test_rate_limit_and_audit_bound_apply_to_invalid_attempts(self):
        for _ in range(phase3.POLICY["session_max_attempts"]):
            self.error(self.gateway.exchange("pacs-read", "wrong"), "forbidden")
        self.error(self.gateway.exchange("audit", self.token), "throttled")
        self.assertLessEqual(self.gateway.retention_status()["events"], phase3.POLICY["audit_max_events"])

    def test_bad_fhir_is_non_reflective_operation_outcome_and_audit(self):
        private_text = b'{"name":"SYNTHETIC_SECRET_MARKER"}'
        self.error(self.gateway.exchange("fhir", self.token, private_text), "invalid")
        audit = self.gateway.exchange("audit", self.token)
        serialized = json.dumps(audit)
        self.assertNotIn("SYNTHETIC_SECRET_MARKER", serialized)
        self.assertNotIn(self.token, serialized)
        self.assertEqual(set(audit["events"][-1]), {"sequence", "time", "operation", "result"})
        self.assertFalse(audit["durable"])
        self.assertFalse(audit["tamper_resistant"])

    def test_bad_hl7_does_not_reflect_control_id_or_construct_unsafe_ack(self):
        raw = lab.hl7_fixture().replace("SYNTHETIC-0001", "SYNTHETIC_SECRET_MARKER").encode("ascii")
        response = self.gateway.exchange("hl7", self.token, raw)
        self.error(response, "invalid")
        self.assertNotIn("ack", response)
        self.assertNotIn("SYNTHETIC_SECRET_MARKER", json.dumps(response))

    def test_unsupported_operation_does_not_enter_audit(self):
        self.error(self.gateway.exchange("SYNTHETIC_SECRET_MARKER", self.token), "forbidden")
        for operation in [None, [], {}, 2]:
            self.error(self.gateway.exchange(operation, self.token), "forbidden")
        self.assertNotIn("SYNTHETIC_SECRET_MARKER", json.dumps(self.gateway.exchange("audit", self.token)))

    def test_successful_fhir_gateway_roundtrip(self):
        raw = json.dumps(bundle()).encode("utf8")
        self.assertEqual(self.gateway.exchange("fhir", self.token, raw), bundle())

    def test_pacs_registered_instance_only_retrieve_exact_pixels_and_hash(self):
        raw = lab.dicom_fixture()
        stored = self.gateway.exchange("pacs-store", self.token, raw)
        self.assertEqual(stored["instance"], lab.UID)
        self.assertEqual(stored["source_sha256"], hashlib.sha256(raw).hexdigest())
        view = self.gateway.exchange("pacs-read", self.token)
        self.assertEqual(view["png"], phase2.secure_view(raw)["png"])
        self.assertFalse(view["pixel_transform"])
        self.assertEqual(self.gateway.retention_status()["instances"], 1)
        self.gateway.exchange("pacs-store", self.token, raw)
        self.assertEqual(self.gateway.retention_status()["instances"], 1)

    def test_pacs_rejects_modified_pixels_without_overwriting_previous(self):
        raw = lab.dicom_fixture()
        self.gateway.exchange("pacs-store", self.token, raw)
        self.error(self.gateway.exchange("pacs-store", self.token, raw[:-1]+bytes([raw[-1]^1])), "invalid")
        self.assertEqual(self.gateway.exchange("pacs-read", self.token)["source_sha256"], hashlib.sha256(raw).hexdigest())

    def test_pacs_ttl_is_enforced_on_access_and_explicit_sweep(self):
        self.gateway.exchange("pacs-store", self.token, lab.dicom_fixture())
        self.now += phase3.POLICY["pacs_ttl_seconds"]
        self.assertEqual(self.gateway.retention_status()["instances"], 0)
        self.error(self.gateway.exchange("pacs-read", self.token), "not-found")
        self.assertEqual(self.gateway.exchange("audit", self.token)["events"][-1]["result"], "not-found")

    def test_no_hospital_or_network_activation_and_payload_policy(self):
        with self.assertRaises(lab.ContractError):self.gateway.connect_operational({"target":"hospital"})
        for operation in ["audit", "pacs-read"]:
            self.error(self.gateway.exchange(operation, self.token, b"unexpected"), "invalid")
        with self.assertRaises(lab.ContractError):phase3.outcome("arbitrary-text")

    def test_audit_ttl_and_close_clear_references_without_erasure_claim(self):
        self.now += phase3.POLICY["audit_ttl_seconds"]
        self.assertEqual(self.gateway.retention_status()["events"], 0)
        self.gateway.close()
        self.assertEqual(self.gateway.retention_status()["instances"], 0)
        self.assertEqual(self.gateway.retention_status()["events"], 0)
        self.error(self.gateway.exchange("audit", self.token), "expired")
        with self.assertRaises(lab.ContractError):self.gateway.issue_lab_credential("reviewer")
        self.assertFalse(phase3.POLICY["secure_erasure_guaranteed"])

    def test_demo_materializes_hashes_no_credentials_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/"new"
            receipt = phase3.demo(output)
            self.assertFalse(receipt["credentials_exported"])
            self.assertFalse(receipt["network_used"])
            self.assertEqual(receipt["visual"], "NOT_EXECUTED_POLICY_BLOCKED")
            for entry in receipt["files"]:
                raw = (output/entry["name"]).read_bytes()
                self.assertEqual(len(raw), entry["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
            self.assertNotIn("token", (output/"audit.json").read_text())
            with self.assertRaises(lab.ContractError):phase3.demo(output)


if __name__ == "__main__":
    unittest.main()
