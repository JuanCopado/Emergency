"""Phase-two synthetic file exchange. No hospital transport or clinical service."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import html
import json
import time
from pathlib import Path

import interop_lab as lab

CONTRACT = "emergency-interop-synthetic-v2"
FIXED_TIME = "2026-11-27T12:00:00Z"
PATIENT = {"resourceType": "Patient", "id": "synthetic-lab", "active": False}
REPORT_CODE = {"coding": [{"system": "urn:emergency:lab:report-code",
                            "code": "synthetic-laboratory-panel",
                            "display": "Synthetic laboratory panel"}]}
POLICY = {
    "contract": CONTRACT, "data": "synthetic-only",
    "authentication": "trusted-local-process-capability; not institutional identity",
    "permissions": ["fhir-read-synthetic", "hl7-read-synthetic", "dicom-render-registered"],
    "session_max_seconds": 300,
    "payload_retention": "no adapter cache; returned QA artifacts remain owner-managed",
    "operational_authentication_approved": False,
    "operational_permissions_approved": False,
    "operational_retention_approved": False,
    "operational_connections_enabled": False,
}


def _report(observation_ids):
    return {"resourceType": "DiagnosticReport", "id": "synthetic-report", "status": "final",
            "code": copy.deepcopy(REPORT_CODE),
            "subject": {"reference": "Patient/synthetic-lab"},
            "effectiveDateTime": FIXED_TIME, "issued": FIXED_TIME,
            "result": [{"reference": "Observation/"+value} for value in observation_ids]}


def _checked_observation(observation):
    lab.require(isinstance(observation, dict), "observation must be an object")
    original_id = observation.get("id")
    normalized = copy.deepcopy(observation)
    normalized["id"] = "synthetic-observation"
    # Reuse the already tested source coding, units, numeric, identity and field guards.
    checked = lab.bundle_for(normalized)["entry"][1]["resource"]
    code = checked["code"]["coding"][0]["code"]
    lab.require(original_id == "synthetic-observation-"+code, "observation identity/code mismatch")
    checked["id"] = original_id
    return checked


def validate_bundle(bundle, version):
    lab.require(version == lab.FHIR_VERSION, "unsupported FHIR version")
    lab.require(len(json.dumps(bundle, allow_nan=False).encode("utf8")) <= lab.MAX_MESSAGE,
                "FHIR size limit")
    lab.exact_keys(bundle, ["resourceType", "id", "type", "meta", "entry"])
    lab.require(bundle["resourceType"] == "Bundle" and bundle["id"] == "synthetic-report-bundle"
                and bundle["type"] == "collection", "unsupported synthetic report bundle")
    expected_meta = {"versionId": "1", "tag": [{"system": "urn:emergency:lab", "code": CONTRACT}]}
    lab.require(bundle["meta"] == expected_meta, "synthetic contract/version required")
    entries = bundle["entry"]
    lab.require(isinstance(entries, list) and 3 <= len(entries) <= 4, "one or two results required")
    for entry in entries:
        lab.exact_keys(entry, ["resource"])
    patient = entries[0]["resource"]
    lab.require(patient == PATIENT and patient.get("active") is False,
                "real patient fields or non-boolean active forbidden")
    observations = [_checked_observation(entry["resource"]) for entry in entries[1:-1]]
    identities = [obs["id"] for obs in observations]
    lab.require(len(set(identities)) == len(identities), "duplicate result identity")
    lab.require(identities == sorted(identities), "canonical result ordering required")
    lab.require(entries[-1]["resource"] == _report(identities),
                "report/result references, subject or fields mismatch")
    return copy.deepcopy(bundle)


def bundle_for_results(results):
    lab.require(isinstance(results, list) and 1 <= len(results) <= 2, "one or two results required")
    observations = []
    for observation in results:
        lab.require(isinstance(observation, dict), "observation must be an object")
        candidate = copy.deepcopy(observation)
        checked = lab.bundle_for(candidate)["entry"][1]["resource"]
        code = checked["code"]["coding"][0]["code"]
        checked["id"] = "synthetic-observation-"+code
        observations.append(checked)
    observations.sort(key=lambda item: item["id"])
    result = {"resourceType": "Bundle", "id": "synthetic-report-bundle", "type": "collection",
              "meta": {"versionId": "1", "tag": [{"system": "urn:emergency:lab", "code": CONTRACT}]},
              "entry": [{"resource": copy.deepcopy(PATIENT)},
                        *[{"resource": value} for value in observations],
                        {"resource": _report([value["id"] for value in observations])}]}
    return validate_bundle(result, lab.FHIR_VERSION)


def hl7_panel_fixture(values=None):
    values = [("718-7", "13.2"), ("2345-7", "100.0")] if values is None else values
    lab.require(isinstance(values, list) and 1 <= len(values) <= 2, "one or two results required")
    source = lab.hl7_fixture().split("\r")
    lines = [source[0].replace("SYNTHETIC-0001", "SYNTHETIC-PHASE2-0001"),
             source[1],
             "OBR|1|SYNTHETIC-ORDER|SYNTHETIC-RESULT|SYNTHETIC-PANEL^Synthetic laboratory panel^L"]
    for index, (code, value) in enumerate(values, 1):
        fields = lab.hl7_fixture(code, value).split("\r")[3].split("|")
        fields[1] = str(index)
        lines.append("|".join(fields))
    return "\r".join(lines)+"\r"


def hl7_panel_to_fhir(raw):
    lab.require(isinstance(raw, bytes) and 0 < len(raw) <= lab.MAX_MESSAGE, "HL7 size/type limit")
    try:
        message = raw.decode("ascii")
    except UnicodeDecodeError:
        raise lab.ContractError("HL7 ASCII subset required") from None
    lab.require(message.endswith("\r") and "\n" not in message and "\x0b" not in message,
                "ER7 CR framing required")
    lines = message[:-1].split("\r")
    lab.require(4 <= len(lines) <= 5, "one panel with one or two results required")
    lab.require(lines[:3] == hl7_panel_fixture()[:-1].split("\r")[:3],
                "header, route, test processing, patient or panel mismatch")
    observations = []
    for index, line in enumerate(lines[3:], 1):
        fields = line.split("|")
        lab.require(len(fields) == 12 and fields[:2] == ["OBX", str(index)],
                    "result sequence/shape mismatch")
        code = fields[3].split("^")[0]
        lab.require(code in lab.CODES, "unsupported result coding")
        baseline = lab.hl7_fixture(code).split("\r")
        fields[1] = "1"
        baseline[3] = "|".join(fields)
        checked = lab.hl7_to_fhir("\r".join(baseline).encode("ascii"))
        observations.append(checked["bundle"]["entry"][1]["resource"])
    result = bundle_for_results(observations)
    ack = lab.hl7_to_fhir(lab.hl7_fixture().encode("ascii"))["ack"]
    ack = ack.replace("SYNTHETIC-ACK-0001", "SYNTHETIC-PHASE2-ACK-0001")
    ack = ack.replace("MSA|AA|SYNTHETIC-0001", "MSA|AA|SYNTHETIC-PHASE2-0001")
    return {"bundle": result, "ack": ack, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "FHIR": lab.FHIR_VERSION, "HL7": lab.HL7_VERSION, "unit_conversion": False}


def secure_view(raw):
    rendered = lab.receive_dicom(raw)
    sha = html.escape(rendered["source_sha256"], quote=True)
    image = base64.b64encode(rendered["png"]).decode("ascii")
    css = ("body{margin:0;background:#111827;color:#fff;font:18px/1.5 system-ui;padding:24px}"
           "main{max-width:1000px;margin:auto}figure{margin:16px 0;padding:16px;border:2px solid #94a3b8}"
           ".enlarged{image-rendering:pixelated;max-width:100%;height:auto}"
           "code{overflow-wrap:anywhere}summary{cursor:pointer}img{background:#000}"
           ".scale-views figure{display:none}.scale-controls label{margin-right:16px}"
           ".scale-controls input:focus-visible+label{outline:3px solid #facc15;outline-offset:4px}"
           "#scale-native:checked~.scale-views #native-pixels{display:block}"
           "#scale-four:checked~.scale-views #four-pixels{display:block}"
           "#scale-eight:checked~.scale-views #eight-pixels{display:block}"
           "@media print{body{background:#fff;color:#000}}")
    style_hash = base64.b64encode(hashlib.sha256(css.encode("utf8")).digest()).decode("ascii")
    policy = ("default-src 'none'; img-src data:; style-src 'sha256-"+style_hash
              +"'; object-src 'none'; base-uri 'none'; form-action 'none'")
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="referrer" content="no-referrer">'
            '<meta http-equiv="Content-Security-Policy" content="'+policy+'">'
            '<title>Synthetic DICOM laboratory</title><style>'+css+'</style></head><body><main>'
            '<h1>Synthetic DICOM laboratory</h1><p><strong>No diagnostic use. CLINICALLY_PENDING.</strong></p>'
            '<p>Registered procedural phantom. 64 × 64 pixels; grayscale 8-bit; no patient image.</p>'
            '<fieldset class="scale-controls" aria-describedby="scale-help">'
            '<legend>Display scale; source pixels unchanged</legend>'
            '<p id="scale-help">Choose a scale with the radio controls. Arrow keys change the selection. '
            'This changes display size only, not image contrast or source pixels. '
            'Scales are nominal CSS sizes and may shrink to fit the viewport; no display calibration.</p>'
            '<input type="radio" name="display-scale" id="scale-native" value="1" checked>'
            '<label for="scale-native">1:1 native pixels</label>'
            '<input type="radio" name="display-scale" id="scale-four" value="4">'
            '<label for="scale-four">4× nearest-neighbour display</label>'
            '<input type="radio" name="display-scale" id="scale-eight" value="8">'
            '<label for="scale-eight">8× nearest-neighbour display</label>'
            '<div class="scale-views"><figure id="native-pixels"><figcaption>Native pixels, 1:1</figcaption><img width="64" height="64" '
            'alt="Native synthetic grayscale phantom" src="data:image/png;base64,'+image+'"></figure>'
            '<figure id="four-pixels"><figcaption>4× nearest-neighbour display; no source pixel modification</figcaption>'
            '<img class="enlarged" width="256" height="256" alt="Four-times synthetic grayscale phantom" '
            'src="data:image/png;base64,'+image+'"></figure>'
            '<figure id="eight-pixels"><figcaption>8× nearest-neighbour display; no source pixel modification</figcaption>'
            '<img class="enlarged" width="512" height="512" alt="Enlarged synthetic grayscale phantom" '
            'src="data:image/png;base64,'+image+'"></figure></div></fieldset>'
            '<details><summary>Technical provenance and limits</summary><p>Source SHA-256: <code>'+sha
            +'</code></p><p>Explicit VR Little Endian. No PACS, hospital connection, '
            'windowing or diagnostic interpretation.</p></details></main></body></html>')
    return {"html": page, "png": rendered["png"], "source_sha256": rendered["source_sha256"],
            "rows": 64, "columns": 64, "pixel_transform": False}


class LocalLabAdapter:
    """Trusted process capability only; never an institutional identity or network credential."""

    def __init__(self, policy, *, seconds=120, permissions=None, clock=time.monotonic):
        lab.require(policy == POLICY, "local policy mismatch or operational prerequisites unapproved")
        lab.require(all(policy[key] is False for key in POLICY if key.startswith("operational_")),
                    "operational controls must be explicitly unapproved")
        lab.require(type(seconds) is int and 1 <= seconds <= POLICY["session_max_seconds"],
                    "invalid capability lifetime")
        selected = POLICY["permissions"] if permissions is None else permissions
        lab.require(isinstance(selected, list) and all(isinstance(item, str) for item in selected),
                    "invalid permissions")
        lab.require(set(selected).issubset(POLICY["permissions"]), "permission escalation forbidden")
        self._permissions = frozenset(selected)
        self._clock = clock
        self._deadline = clock()+seconds
        self._capability = object()

    def capability(self):
        lab.require(self._capability is not None, "local session closed")
        return self._capability

    def _authorize(self, operation, capability):
        if self._clock() >= self._deadline:
            self.close()
        lab.require(self._capability is not None and capability is self._capability,
                    "capability missing, expired or from another session")
        lab.require(operation in self._permissions, "operation not permitted")

    def receive_fhir(self, raw, capability):
        self._authorize("fhir-read-synthetic", capability)
        lab.require(isinstance(raw, bytes) and len(raw) <= lab.MAX_MESSAGE, "FHIR size/type limit")
        parsed = json.loads(raw, object_pairs_hook=lab._unique_object,
                            parse_int=lab.lossless_number, parse_float=lab.lossless_number)
        return validate_bundle(parsed, lab.FHIR_VERSION)

    def receive_hl7(self, raw, capability):
        self._authorize("hl7-read-synthetic", capability)
        return hl7_panel_to_fhir(raw)

    def receive_dicom(self, raw, capability):
        self._authorize("dicom-render-registered", capability)
        return secure_view(raw)

    def close(self):
        self._capability = None

    def connect_operational(self, _request):
        raise lab.ContractError("hospital transport disabled; identity, permissions, retention and security unapproved")


def demo(output):
    session = LocalLabAdapter(copy.deepcopy(POLICY))
    capability = session.capability()
    raw = hl7_panel_fixture().encode("ascii")
    converted = session.receive_hl7(raw, capability)
    encoded = (json.dumps(converted["bundle"], indent=2)+"\n").encode("utf8")
    verified = session.receive_fhir(encoded, capability)
    lab.require(verified == converted["bundle"], "local roundtrip mismatch")
    viewed = session.receive_dicom(lab.dicom_fixture(), capability)
    root = lab.local_path(output)
    lab.require(not root.exists(), "output directory must be new")
    root.mkdir(parents=True)
    outputs = {"panel.hl7": raw, "bundle.json": encoded,
               "ack.hl7": converted["ack"].encode("ascii"),
               "phantom.dcm": lab.dicom_fixture(), "image.png": viewed["png"],
               "viewer.html": viewed["html"].encode("utf8"),
               "LOCAL_POLICY.json": (json.dumps(POLICY, indent=2)+"\n").encode("utf8")}
    records = []
    for name, value in outputs.items():
        lab._new_file(root/name, value)
        records.append({"name": name, "bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()})
    session.close()
    receipt = {"contract": CONTRACT, "base": "a3ae85412a868c105c64ca8b491e1cb3a1df065c",
               "resources": ["Patient", "Observation", "DiagnosticReport"], "observations": 2,
               "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE",
               "operational_connection": False, "patient_data": False, "unit_conversion": False,
               "session_closed": True, "payload_cache": False,
               "artifact_retention": "owner-managed synthetic QA evidence; no automatic erasure claim",
               "files": records}
    lab._new_file(root/"RECEIPT.json", (json.dumps(receipt, indent=2)+"\n").encode("utf8"))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new local demonstration output directory")
    args = parser.parse_args()
    try:
        print(json.dumps(demo(args.output), indent=2))
    except (lab.ContractError, OSError, ValueError, RecursionError):
        parser.exit(2, "synthetic phase-two exchange rejected; no input content logged\n")
