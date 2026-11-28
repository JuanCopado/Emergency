import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import interop_lab as lab
import interop_phase2 as phase2


class ReportExchangeTests(unittest.TestCase):
    def bundle(self):
        return phase2.bundle_for_results([lab.synthetic_observation("718-7",13.2),
                                         lab.synthetic_observation("2345-7",100.0)])

    def reject(self, mutation):
        result=self.bundle();mutation(result)
        with self.assertRaises((lab.ContractError, ValueError)):
            phase2.validate_bundle(result,lab.FHIR_VERSION)

    def test_patient_observations_report_linked_and_immutable(self):
        bundle=self.bundle();original=copy.deepcopy(bundle)
        validated=phase2.validate_bundle(bundle,lab.FHIR_VERSION)
        resources=[entry["resource"] for entry in validated["entry"]]
        self.assertEqual([r["resourceType"] for r in resources],
                         ["Patient","Observation","Observation","DiagnosticReport"])
        self.assertEqual(resources[-1]["result"],
                         [{"reference":"Observation/"+r["id"]} for r in resources[1:-1]])
        validated["entry"][0]["resource"]["id"]="modified"
        self.assertEqual(bundle,original)

    def test_one_result_supported_without_inventing_another(self):
        bundle=phase2.bundle_for_results([lab.synthetic_observation()])
        self.assertEqual(len(bundle["entry"]),3)
        self.assertEqual(len(bundle["entry"][-1]["resource"]["result"]),1)

    def test_empty_duplicate_excess_or_wrong_type_results_rejected(self):
        for result in [[],[lab.synthetic_observation()]*2,[lab.synthetic_observation()]*3,[None]]:
            with self.subTest(result=result):
                with self.assertRaises(lab.ContractError):phase2.bundle_for_results(result)

    def test_report_external_missing_extra_or_duplicate_reference_rejected(self):
        for references in [[{"reference":"https://invalid.example/Observation/1"}],[],
                           [{"reference":"Observation/synthetic-observation-718-7"}]*2]:
            with self.subTest(references=references):
                self.reject(lambda b:b["entry"][-1]["resource"].update(result=references))

    def test_real_patient_report_subject_and_narrative_rejected(self):
        self.reject(lambda b:b["entry"][0]["resource"].update(name=[{"text":"person"}]))
        self.reject(lambda b:b["entry"][0]["resource"].update(active=0))
        self.reject(lambda b:b["entry"][-1]["resource"].update(subject={"reference":"Patient/other"}))
        self.reject(lambda b:b["entry"][-1]["resource"].update(conclusion="Give a drug"))
        self.reject(lambda b:b["entry"][-1]["resource"].update(text={"div":"<script>bad</script>"}))

    def test_wrong_version_order_metadata_or_identity_rejected(self):
        with self.assertRaises(lab.ContractError):phase2.validate_bundle(self.bundle(),"5.0.0")
        self.reject(lambda b:b["entry"].reverse())
        self.reject(lambda b:b["meta"].update(versionId="2"))
        self.reject(lambda b:b["entry"][1]["resource"].update(id="synthetic-observation-other"))

    def test_code_units_value_and_malformed_resource_guards_reused(self):
        self.reject(lambda b:b["entry"][1]["resource"]["valueQuantity"].update(code="g/L"))
        self.reject(lambda b:b["entry"][1]["resource"]["code"]["coding"][0].update(code=[]))
        self.reject(lambda b:b["entry"][1].update(resource=None))
        self.reject(lambda b:b["entry"].append({"resource":{"resourceType":"MedicationRequest"}}))


class HL7PanelTests(unittest.TestCase):
    def test_two_results_to_diagnostic_report_and_ack(self):
        raw=phase2.hl7_panel_fixture().encode("ascii")
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            result=phase2.hl7_panel_to_fhir(raw)
        resources=[entry["resource"] for entry in result["bundle"]["entry"]]
        values={r["code"]["coding"][0]["code"]:r["valueQuantity"] for r in resources[1:-1]}
        self.assertEqual(values["718-7"]["value"],13.2)
        self.assertEqual(json.dumps(values["2345-7"]["value"]),"100.0")
        self.assertEqual(values["718-7"]["system"],lab.UCUM)
        self.assertIn("MSA|AA|SYNTHETIC-PHASE2-0001",result["ack"])
        self.assertEqual(result["source_sha256"],hashlib.sha256(raw).hexdigest())

    def test_single_result_no_phantom_extra_result(self):
        result=phase2.hl7_panel_to_fhir(phase2.hl7_panel_fixture([("718-7","13.0")]).encode("ascii"))
        self.assertEqual(len(result["bundle"]["entry"]),3)
        self.assertEqual(json.dumps(result["bundle"]["entry"][1]["resource"]["valueQuantity"]["value"]),"13.0")

    def test_precision_loss_units_coding_or_status_rejected(self):
        base=phase2.hl7_panel_fixture()
        mutations=[base.replace("|13.2|","|13.20|"),base.replace("|13.2|","|-0|"),
                   base.replace("g/dL^g/dL^UCUM","g/L^g/L^UCUM"),
                   base.replace("718-7^Hemoglobin","9999-9^Hemoglobin"),
                   base.replace("|||||F","|||||P")]
        for text in mutations:
            with self.assertRaises(lab.ContractError):phase2.hl7_panel_to_fhir(text.encode("ascii"))

    def test_duplicate_codes_out_of_order_obx_extra_segment_and_framing_rejected(self):
        for text in [phase2.hl7_panel_fixture([("718-7","13.2"),("718-7","14.2")]),
                     phase2.hl7_panel_fixture().replace("OBX|2|","OBX|3|"),
                     phase2.hl7_panel_fixture()+"NTE|1||instruction\r",
                     phase2.hl7_panel_fixture().replace("\r","\n")]:
            with self.assertRaises(lab.ContractError):phase2.hl7_panel_to_fhir(text.encode("ascii"))

    def test_wrong_route_patient_test_mode_and_version_rejected(self):
        for before,after in [("SYNTHETIC-LAB","OTHER-PERSON"),("|T|","|P|"),
                             ("2.5.1","2.3"),("EMERGENCY_LAB","REMOTE"),
                             ("SYNTHETIC-PANEL","OTHER-PANEL")]:
            with self.assertRaises(lab.ContractError):
                phase2.hl7_panel_to_fhir(phase2.hl7_panel_fixture().replace(before,after).encode("ascii"))

    def test_oversize_non_ascii_malformed_obx_rejected(self):
        for raw in [b"x"*65537,b"\xff\r",phase2.hl7_panel_fixture().replace("OBX|1|NM","OBX|1|ST|extra").encode()]:
            with self.assertRaises(lab.ContractError):phase2.hl7_panel_to_fhir(raw)


class LocalCapabilityTests(unittest.TestCase):
    def test_fhir_roundtrip_and_precision_boundary_without_network(self):
        session=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY))
        capability=session.capability()
        encoded=json.dumps(phase2.bundle_for_results([lab.synthetic_observation()])).encode("utf8")
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            self.assertEqual(session.receive_fhir(encoded,capability),json.loads(encoded))
        lossy=encoded.replace(b'"value": 13.2',b'"value": 13.20')
        with self.assertRaises(lab.ContractError):session.receive_fhir(lossy,capability)
        session.close()
        with self.assertRaises(lab.ContractError):session.capability()

    def test_duplicate_json_wrong_type_or_size_rejected(self):
        session=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY));key=session.capability()
        for raw in [b'{"a":1,"a":2}',b"x"*65537,"string"]:
            with self.assertRaises((lab.ContractError,ValueError)):session.receive_fhir(raw,key)

    def test_permission_subset_other_session_and_forged_capability_rejected(self):
        first=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY),permissions=["fhir-read-synthetic"])
        second=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY))
        with self.assertRaises(lab.ContractError):first.receive_dicom(lab.dicom_fixture(),first.capability())
        with self.assertRaises(lab.ContractError):first.receive_hl7(b"",second.capability())
        with self.assertRaises(lab.ContractError):first.receive_hl7(b"",object())

    def test_policy_approval_flags_escalation_and_lifetime_fail_closed(self):
        for field in ["operational_connections_enabled","operational_authentication_approved",
                      "operational_retention_approved","operational_permissions_approved"]:
            candidate=copy.deepcopy(phase2.POLICY);candidate[field]=True
            with self.assertRaises(lab.ContractError):phase2.LocalLabAdapter(candidate)
        with self.assertRaises(lab.ContractError):
            phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY),permissions=["connect-hospital"])
        with self.assertRaises(lab.ContractError):
            phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY),permissions="fhir-read-synthetic")
        candidate=copy.deepcopy(phase2.POLICY);candidate["operational_connections_enabled"]=0
        with self.assertRaises(lab.ContractError):phase2.LocalLabAdapter(candidate)
        for seconds in [0,301,True]:
            with self.assertRaises(lab.ContractError):phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY),seconds=seconds)

    def test_expired_closed_and_operational_connection_never_authorized(self):
        current=[0]
        session=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY),seconds=10,clock=lambda:current[0])
        key=session.capability();current[0]=10
        with self.assertRaises(lab.ContractError):session.receive_hl7(b"",key)
        with self.assertRaises(lab.ContractError):session.receive_hl7(b"",None)
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            with self.assertRaises(lab.ContractError):session.connect_operational({"endpoint":"https://invalid.example"})
        self.assertFalse(any("payload" in name for name in vars(session)))


class DICOMViewerTests(unittest.TestCase):
    def test_responsive_static_view_preserves_png_and_source_hash(self):
        raw=lab.dicom_fixture()
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            session=phase2.LocalLabAdapter(copy.deepcopy(phase2.POLICY))
            result=session.receive_dicom(raw,session.capability())
        self.assertEqual(result["png"],lab.receive_dicom(raw)["png"])
        self.assertEqual(result["source_sha256"],hashlib.sha256(raw).hexdigest())
        self.assertIn('lang="en"',result["html"])
        self.assertIn('name="viewport"',result["html"])
        self.assertIn("image-rendering:pixelated",result["html"])
        self.assertIn("Native pixels, 1:1",result["html"])
        self.assertIn("style-src 'sha256-",result["html"])
        self.assertNotIn("<script",result["html"])
        self.assertNotIn("https://",result["html"])
        self.assertNotIn("SYNTHETIC^PHANTOM",result["html"])
        self.assertFalse(result["pixel_transform"])

    def test_spoofed_synthetic_pixels_and_active_payload_rejected(self):
        raw=bytearray(lab.dicom_fixture());raw[-1]^=1
        for data in [bytes(raw),b"<svg><script>bad</script></svg>"]:
            with self.assertRaises(lab.ContractError):phase2.secure_view(data)

    def test_demo_materializes_all_formats_and_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"phase2"
            with patch("socket.socket",side_effect=AssertionError("network forbidden")):
                result=phase2.demo(out)
            self.assertEqual(result["observations"],2)
            self.assertFalse(result["operational_connection"])
            for record in result["files"]:
                data=(out/record["name"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(),record["sha256"])
            with self.assertRaises(lab.ContractError):phase2.demo(out)


if __name__=="__main__":unittest.main()
