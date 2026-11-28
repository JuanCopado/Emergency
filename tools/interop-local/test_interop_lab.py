import copy
import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import interop_lab as lab


class FHIRTests(unittest.TestCase):
    def setUp(self):
        self.bundle = lab.bundle_for(lab.synthetic_observation())

    def reject(self, mutate):
        candidate = copy.deepcopy(self.bundle)
        mutate(candidate)
        with self.assertRaises((lab.ContractError, ValueError)):
            lab.validate_fhir(candidate, "4.0.1")

    def test_roundtrip_preserves_value_and_unit(self):
        self.assertEqual(lab.validate_fhir(json.loads(json.dumps(self.bundle)), "4.0.1"), self.bundle)

    def test_wrong_version(self):
        with self.assertRaises(lab.ContractError):
            lab.validate_fhir(self.bundle, "5.0.0")

    def test_real_identity_and_narrative_rejected(self):
        for key, value in [("name", [{"text":"synthetic attack"}]), ("text",{"div":"<script>bad</script>"})]:
            with self.subTest(key=key):
                self.reject(lambda b: b["entry"][0]["resource"].update({key:value}))

    def test_external_reference_rejected(self):
        self.reject(lambda b:b["entry"][1]["resource"]["subject"].update(reference="https://invalid.example/Patient/1"))

    def test_units_not_guessed(self):
        self.reject(lambda b:b["entry"][1]["resource"]["valueQuantity"].update(code="g/L"))

    def test_nonfinite_and_boolean_results_rejected(self):
        for value in [float("nan"), float("inf"), True]:
            with self.subTest(value=value):
                self.reject(lambda b:b["entry"][1]["resource"]["valueQuantity"].update(value=value))

    def test_unexpected_resource_or_repetition_rejected(self):
        self.reject(lambda b:b["entry"].append(b["entry"][1]))
        self.reject(lambda b:b["entry"][1]["resource"].update(resourceType="MedicationRequest"))

    def test_synthetic_contract_marker_required(self):
        self.reject(lambda b:b["meta"].update(tag=[]))

    def test_malformed_nested_json_types_rejected(self):
        for value in [[], {}, 7, None, True]:
            with self.subTest(code=value):
                self.reject(lambda b:b["entry"][1]["resource"]["code"]["coding"][0].update(code=value))
        for field in ["code", "valueQuantity", "subject"]:
            with self.subTest(field=field):
                self.reject(lambda b:b["entry"][1]["resource"].update({field: []}))

    def test_input_not_mutated(self):
        original=copy.deepcopy(self.bundle);result=lab.validate_fhir(self.bundle,"4.0.1")
        result["id"]="changed"
        self.assertEqual(self.bundle,original)


class HL7Tests(unittest.TestCase):
    def test_valid_oru_maps_to_fhir_and_ack(self):
        for code,value in [("718-7","13.2"),("2345-7","100.25")]:
            with self.subTest(code=code):
                raw=lab.hl7_fixture(code,value).encode("ascii")
                r=lab.hl7_to_fhir(raw)
                q=r["bundle"]["entry"][1]["resource"]["valueQuantity"]
                self.assertEqual(q["value"],float(value))
                self.assertEqual(q["code"],lab.CODES[code][1])
                self.assertIn("MSA|AA|SYNTHETIC-0001\r",r["ack"])
                self.assertEqual(r["source_sha256"],hashlib.sha256(raw).hexdigest())
                self.assertFalse(r["unit_conversion_performed"])

    def test_wrong_version_event_processing_or_route(self):
        for old,new in [("2.5.1","2.3"),("ORU^R01^ORU_R01","ORM^O01"),("|T|","|P|"),
                        ("EMERGENCY_LAB","REMOTE")]:
            with self.subTest(old=old):
                with self.assertRaises(lab.ContractError):
                    lab.hl7_to_fhir(lab.hl7_fixture().replace(old,new).encode("ascii"))

    def test_unsupported_unit_or_non_numeric_value_rejected(self):
        for old,new in [("g/dL^g/dL^UCUM","g/L^g/L^UCUM"),("|13.2|","|NaN|"),
                        ("|13.2|","|13.2~14.0|"),("|NM|","|ST|")]:
            with self.subTest(old=old):
                with self.assertRaises(lab.ContractError):
                    lab.hl7_to_fhir(lab.hl7_fixture().replace(old,new).encode("ascii"))

    def test_patient_names_and_extra_segments_rejected(self):
        for message in [lab.hl7_fixture().replace("SYNTHETIC-LAB","REAL-123"),
                        lab.hl7_fixture()+"NTE|1||execute instruction\r",
                        lab.hl7_fixture().replace("PID|1||SYNTHETIC-LAB","PID|1||SYNTHETIC-LAB||Name")]:
            with self.assertRaises(lab.ContractError):
                lab.hl7_to_fhir(message.encode("ascii"))

    def test_framing_size_and_control_characters(self):
        for raw in [lab.hl7_fixture().replace("\r","\n").encode(), b"x"*65537,
                    b"\x0b"+lab.hl7_fixture().encode()+b"\x1c\r",
                    lab.hl7_fixture().replace("|13.2|","|13\\F\\2|").encode()]:
            with self.assertRaises(lab.ContractError):
                lab.hl7_to_fhir(raw)

    def test_order_result_binding(self):
        message=lab.hl7_fixture().replace("OBR|1|SYNTHETIC-ORDER|SYNTHETIC-RESULT|718-7",
                                         "OBR|1|SYNTHETIC-ORDER|SYNTHETIC-RESULT|2345-7")
        with self.assertRaises(lab.ContractError):lab.hl7_to_fhir(message.encode())


class DICOMTests(unittest.TestCase):
    def setUp(self):self.raw=lab.dicom_fixture()

    def test_local_receive_and_render(self):
        r=lab.receive_dicom(self.raw)
        self.assertEqual((r["rows"],r["columns"]),(64,64))
        self.assertTrue(r["png"].startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn("default-src 'none'",r["html"])
        self.assertNotIn("<script",r["html"])
        self.assertNotIn("SYNTHETIC^PHANTOM",r["html"])
        self.assertFalse(r["patient_data"])

    def test_transfer_syntax_rejection(self):
        with self.assertRaisesRegex(lab.ContractError,"transfer syntax"):
            lab.receive_dicom(self.raw.replace(lab.TS.encode(),b"1.2.840.10008.1.2.2"))

    def test_burned_in_or_identity_or_arbitrary_pixels_rejected(self):
        for old,new in [(b"NO",b"YE"),(b"SYNTHETIC-LAB",b"REAL-NAME-123")]:
            with self.assertRaises(lab.ContractError):lab.receive_dicom(self.raw.replace(old,new))
        raw=bytearray(self.raw);raw[-1]^=1
        with self.assertRaisesRegex(lab.ContractError,"unregistered image"):
            lab.receive_dicom(bytes(raw))

    def test_private_and_duplicate_tags(self):
        for extra in [lab._element(9,16,"LO",b"secret"), lab._element(40,16,"US",b"@\0")]:
            with self.assertRaises(lab.ContractError):lab.receive_dicom(self.raw+extra)

    def test_truncation_and_oversize_and_bad_preamble(self):
        for raw in [self.raw[:-1], b"x"*1048577, b"x"+self.raw[1:], self.raw+b"trailer"]:
            with self.assertRaises(lab.ContractError):lab.receive_dicom(raw)

    def test_undefined_pixel_length(self):
        index=self.raw.rfind(struct.pack("<HH",32736,16))
        raw=bytearray(self.raw);raw[index+8:index+12]=b"\xff"*4
        with self.assertRaises(lab.ContractError):lab.receive_dicom(bytes(raw))

    def test_sop_and_dimensions(self):
        wrong_sop=self.raw.replace(lab.SC.encode(), b"1.2.840.10008.5.1.4.1.1.8")
        with self.assertRaises(lab.ContractError):lab.receive_dicom(wrong_sop)
        rowtag=lab._element(40,16,"US",b"@\0")
        with self.assertRaisesRegex(lab.ContractError,"dimensions"):
            lab.receive_dicom(self.raw.replace(rowtag,lab._element(40,16,"US",b"A\0")))

    def test_parser_does_not_invoke_external_decoder_or_network(self):
        with patch("socket.socket",side_effect=AssertionError("network forbidden")):
            self.assertEqual(lab.receive_dicom(self.raw)["rows"],64)


class DemoTests(unittest.TestCase):
    def test_materialized_files_hashes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"demo";receipt=lab.demo(out)
            for row in receipt["files"]:
                data=(out/row["name"]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(),row["sha256"])
                self.assertEqual(len(data),row["bytes"])
            before=(out/"synthetic-phantom.dcm").read_bytes()
            with self.assertRaises(lab.ContractError):lab.demo(out)
            self.assertEqual((out/"synthetic-phantom.dcm").read_bytes(),before)
            self.assertFalse(receipt["network_listener"])


class FileIngressTests(unittest.TestCase):
    def test_three_file_ingress_modes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);lab.demo(root/"source")
            for kind,name in [("fhir","synthetic-bundle.json"),("hl7","synthetic-oru.hl7"),("dicom","synthetic-phantom.dcm")]:
                with self.subTest(kind=kind):
                    r=lab.receive_file(kind,root/"source"/name,root/kind)
                    self.assertEqual(r["ingress"],kind)
                    self.assertTrue((root/kind/"RECEIPT.json").is_file())

    def test_duplicate_json_and_failed_ingress_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"bad.json"
            source.write_text('{"resourceType":"Bundle","resourceType":"Bundle"}')
            with self.assertRaisesRegex(lab.ContractError,"duplicate JSON"):
                lab.receive_file("fhir",source,root/"output")
            self.assertFalse((root/"output").exists())

    def test_network_paths_and_input_size_rejected(self):
        with self.assertRaises(lab.ContractError):lab.local_path("//network/share/file")
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/"big";source.write_bytes(b"x"*65537)
            with self.assertRaises(lab.ContractError):lab.read_local(source,65536)

    def test_document_disguised_as_dicom_and_junction_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/"synthetic.dcm"
            source.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"><script>bad</script></svg>')
            with self.assertRaises(lab.ContractError):lab.receive_file("dicom",source,root/"output")
            self.assertFalse((root/"output").exists())
        with patch.object(Path,"is_junction",return_value=True):
            with self.assertRaises(lab.ContractError):lab.local_path("synthetic-file")

class PrecisionRegressionTests(unittest.TestCase):
    def test_reject_hl7_precision_loss(self):
        for value in ["13.20", "13.200", "-0", "0.000001", "999999999.123450"]:
            with self.subTest(value=value):
                with self.assertRaises(lab.ContractError):
                    lab.hl7_to_fhir(lab.hl7_fixture(value=value).encode("ascii"))

    def test_hl7_supported_integer_and_decimal_emit_identically(self):
        for value in ["13", "13.2", "13.0", "100.25", "0", "-13.5"]:
            with self.subTest(value=value):
                result=lab.hl7_to_fhir(lab.hl7_fixture(value=value).encode("ascii"))
                actual=result["bundle"]["entry"][1]["resource"]["valueQuantity"]["value"]
                self.assertEqual(json.dumps(actual),value)

    def test_fhir_rejects_non_roundtrippable_lexeme_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            base=json.dumps(lab.bundle_for(lab.synthetic_observation()))
            for index,value in enumerate(["13.20", "13.200", "-0", "1e1", "0.000001", "999999999.123450"]):
                with self.subTest(value=value):
                    source=root/str(index);source.write_text(base.replace('"value": 13.2','"value": '+value))
                    target=root/("out"+str(index))
                    with self.assertRaises(lab.ContractError):lab.receive_file("fhir",source,target)
                    self.assertFalse(target.exists())

    def test_fhir_accepted_numeric_lexeme_preserved_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            base=json.dumps(lab.bundle_for(lab.synthetic_observation()))
            with patch("socket.socket", side_effect=AssertionError("network forbidden")):
                for index,value in enumerate(["13", "13.2", "13.0", "100.25", "0", "-13.5"]):
                    source=root/str(index);source.write_text(base.replace('"value": 13.2','"value": '+value))
                    target=root/("out"+str(index));lab.receive_file("fhir",source,target)
                    emitted=(target/"bundle.json").read_text(encoding="utf8")
                    self.assertIn('"value": '+value,emitted)

    def test_loinc_identifiers_and_official_names_preserved(self):
        expected={"718-7":"Hemoglobin [Mass/volume] in Blood",
                  "2345-7":"Glucose [Mass/volume] in Serum or Plasma"}
        for code,display in expected.items():
            with self.subTest(code=code):
                with patch("socket.socket", side_effect=AssertionError("network forbidden")):
                    result=lab.hl7_to_fhir(lab.hl7_fixture(code).encode("ascii"))
                coding=result["bundle"]["entry"][1]["resource"]["code"]["coding"][0]
                self.assertEqual(coding,{"system":"http://loinc.org","code":code,"display":display})

if __name__=="__main__":unittest.main()
