import base64
import contextlib
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import interop_lab as lab
import interop_phase2 as phase2
import interop_phase3 as phase3
import interop_exchange as exchange


def pair(values=None):
    hl7 = phase2.hl7_panel_fixture(values).encode("ascii")
    fhir = json.dumps(phase3.receive_hl7(hl7)["bundle"]).encode("utf8")
    return fhir, hl7


class DiagnosticPairTests(unittest.TestCase):
    def test_matching_single_and_panel_keep_exact_output_and_provenance(self):
        for hl7 in [lab.hl7_fixture().encode("ascii"), phase2.hl7_panel_fixture().encode("ascii")]:
            fhir = json.dumps(phase3.receive_hl7(hl7)["bundle"]).encode("utf8")
            result = exchange.reconcile(fhir, hl7)
            self.assertEqual(result["bundle"], phase3.decode_fhir(fhir))
            self.assertEqual(result["ack"], phase3.receive_hl7(hl7)["ack"])
            self.assertEqual(result["source_sha256"], {"FHIR": hashlib.sha256(fhir).hexdigest(),
                                                        "HL7": hashlib.sha256(hl7).hexdigest()})
            self.assertEqual(result["result_count"], len(result["bundle"]["entry"])-3)
            self.assertFalse(result["unit_conversion"])
            self.assertFalse(result["network_used"])

    def test_two_valid_formats_with_different_results_are_rejected(self):
        fhir, hl7 = pair()
        other = hl7.replace(b"|13.2|", b"|13.3|")
        phase3.decode_fhir(fhir);phase3.receive_hl7(other)
        with self.assertRaisesRegex(lab.ContractError, "^synthetic diagnostic exchange rejected$"):
            exchange.reconcile(fhir, other)

    def test_explicit_pair_contract_preserves_numeric_lexeme_without_changing_base(self):
        fhir, hl7 = pair([("2345-7", "100.0")])
        different = fhir.replace(b'"value": 100.0', b'"value": 100')
        # Both remain valid independently; only the optional exact-pair API rejects the mismatch.
        phase3.decode_fhir(different);phase3.receive_hl7(hl7)
        with self.assertRaises(lab.ContractError):exchange.reconcile(different, hl7)
        result = exchange.reconcile(fhir, hl7)
        obs = result["bundle"]["entry"][2]["resource"]
        self.assertEqual(json.dumps(obs["valueQuantity"]["value"]), "100.0")

    def test_valid_but_missing_corresponding_result_rejected(self):
        fhir, _ = pair()
        _, single = pair([("718-7", "13.2")])
        phase3.receive_hl7(single)
        with self.assertRaises(lab.ContractError):exchange.reconcile(fhir, single)

    def test_json_whitespace_and_key_order_are_not_artificial_mismatches(self):
        fhir, hl7 = pair()
        reordered = json.dumps(json.loads(fhir), sort_keys=True, indent=4).encode("utf8")
        self.assertEqual(exchange.reconcile(reordered, hl7)["bundle"], json.loads(fhir))

    def test_duplicate_keys_external_references_and_malformed_input_not_reflected(self):
        fhir, hl7 = pair()
        external = json.loads(fhir)
        external["entry"][-1]["resource"]["result"] = [{"reference": "https://invalid.example/private-marker"}]
        cases = [(None, hl7), (fhir, None), (b"SYNTHETIC_PRIVATE_MARKER", hl7),
                 (fhir, b"SYNTHETIC_PRIVATE_MARKER"),
                 (fhir.replace(b'"active": false', b'"active": false, "active": false'), hl7),
                 (json.dumps(external).encode("utf8"), hl7),
                 (b"x"*(lab.MAX_MESSAGE+1), hl7)]
        for left, right in cases:
            with self.subTest(kind=type(left).__name__):
                with self.assertRaises(lab.ContractError) as err:exchange.reconcile(left, right)
                self.assertEqual(str(err.exception), "synthetic diagnostic exchange rejected")

    def test_units_and_codes_still_guarded_before_pair_comparison(self):
        fhir, hl7 = pair()
        for invalid in [hl7.replace(b"g/dL", b"g/L"), hl7.replace(b"718-7", b"9999-9")]:
            with self.assertRaises(lab.ContractError):exchange.reconcile(fhir, invalid)

    def test_no_network_and_inputs_not_mutated(self):
        fhir, hl7 = pair();before = (fhir, hl7)
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            self.assertEqual(exchange.reconcile(fhir, hl7)["status"], "MATCHED_SYNTHETIC_EXCHANGE")
        self.assertEqual((fhir, hl7), before)

    def test_cli_writes_new_receipt_refuses_overwrite_and_failed_pair_leaves_no_output(self):
        fhir, hl7 = pair()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder);left=root/"fhir.json";right=root/"hl7.hl7";out=root/"receipt.json"
            left.write_bytes(fhir);right.write_bytes(hl7)
            args = ["--fhir", str(left), "--hl7", str(right), "--output", str(out)]
            with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(exchange.main(args), 0)
            receipt = out.read_bytes()
            self.assertEqual(json.loads(receipt)["bundle"], json.loads(fhir))
            with self.assertRaises(FileExistsError):exchange.write_receipt(left, right, out)
            self.assertEqual(out.read_bytes(), receipt)
            right.write_bytes(hl7.replace(b"|13.2|", b"|13.3|"))
            failed = root/"must-not-exist.json"
            with self.assertRaises(lab.ContractError):exchange.write_receipt(left, right, failed)
            self.assertFalse(failed.exists())
            self.assertEqual(left.read_bytes(), fhir)

    def test_cli_error_is_static_and_does_not_reflect_file_or_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"SYNTHETIC_PRIVATE_MARKER.json";path.write_bytes(b"private-marker")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as code:
                exchange.main(["--fhir", str(path), "--hl7", str(path),
                               "--output", str(Path(folder)/"new.json")])
            self.assertEqual(code.exception.code, 2)
            self.assertNotIn("PRIVATE_MARKER", stderr.getvalue())
            self.assertEqual(stderr.getvalue(),
                             "synthetic diagnostic exchange rejected; no input content logged\n")


class ViewerDOM(HTMLParser):
    def __init__(self):
        super().__init__();self.elements=[];self.style=[];self.in_style=False
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)));self.in_style = tag=="style" or self.in_style
    def handle_endtag(self, tag):
        if tag=="style":self.in_style=False
    def handle_data(self, value):
        if self.in_style:self.style.append(value)


class ViewerContractTests(unittest.TestCase):
    def setUp(self):
        self.raw=lab.dicom_fixture();self.view=phase2.secure_view(self.raw)
        self.dom=ViewerDOM();self.dom.feed(self.view["html"])

    def test_native_radio_controls_are_labelled_grouped_and_have_one_default(self):
        radios=[attrs for tag,attrs in self.dom.elements if tag=="input"]
        self.assertEqual(len(radios), 3)
        self.assertEqual({x["type"] for x in radios}, {"radio"})
        self.assertEqual({x["name"] for x in radios}, {"display-scale"})
        self.assertEqual({x["value"] for x in radios}, {"1", "4", "8"})
        self.assertEqual([x["value"] for x in radios if "checked" in x], ["1"])
        labels=[attrs["for"] for tag,attrs in self.dom.elements if tag=="label"]
        self.assertEqual(set(labels), {x["id"] for x in radios})
        self.assertTrue(any(tag=="legend" for tag,_ in self.dom.elements))
        self.assertTrue(any(tag=="fieldset" and a.get("aria-describedby")=="scale-help"
                            for tag,a in self.dom.elements))
        self.assertTrue(any(a.get("id")=="scale-help" for _,a in self.dom.elements))
        self.assertIn("nominal CSS sizes", self.view["html"])
        self.assertIn("no display calibration", self.view["html"])

    def test_all_scales_render_identical_registered_png_without_transform(self):
        images=[a for tag,a in self.dom.elements if tag=="img"]
        self.assertEqual({(a["width"],a["height"]) for a in images},
                         {("64","64"),("256","256"),("512","512")})
        for image in images:
            self.assertTrue(image["alt"])
            self.assertEqual(base64.b64decode(image["src"].split(",",1)[1]), self.view["png"])
        self.assertEqual(self.view["png"], lab.receive_dicom(self.raw)["png"])
        self.assertEqual(self.view["source_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertFalse(self.view["pixel_transform"])

    def test_strict_csp_matches_actual_css_and_contains_no_active_or_remote_content(self):
        css="".join(self.dom.style)
        digest=base64.b64encode(hashlib.sha256(css.encode("utf8")).digest()).decode("ascii")
        policy=next(a["content"] for tag,a in self.dom.elements
                    if tag=="meta" and a.get("http-equiv")=="Content-Security-Policy")
        self.assertIn("style-src 'sha256-"+digest+"'",policy)
        self.assertIn("default-src 'none'",policy)
        self.assertIn("form-action 'none'",policy)
        self.assertFalse(any(t in {"script","iframe","object","form","a"} for t,_ in self.dom.elements))
        self.assertFalse(any(k.startswith("on") for _,a in self.dom.elements for k in a))
        self.assertIn(":focus-visible",css)
        for identity in ["scale-native","scale-four","scale-eight"]:
            self.assertIn("#"+identity+":checked~.scale-views",css)

    def test_pacs_gateway_uses_same_updated_viewer_and_retains_auth_boundary(self):
        gateway=phase3.SyntheticGateway()
        token=gateway.issue_lab_credential("technician")
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            gateway.exchange("pacs-store",token,self.raw)
            view=gateway.exchange("pacs-read",token)
        self.assertEqual(view["html"],self.view["html"])
        self.assertEqual(gateway.exchange("pacs-read","wrong"),phase3.outcome("forbidden"))
        self.assertIn("No diagnostic use. CLINICALLY_PENDING.",view["html"])
        gateway.close()


if __name__=="__main__":
    unittest.main()
