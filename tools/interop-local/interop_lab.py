"""Closed synthetic interchange laboratory. No sockets, patient ingestion or prescribing."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import math
import re
import struct
import zlib
from pathlib import Path

FHIR_VERSION = "4.0.1"
HL7_VERSION = "2.5.1"
CONTRACT = "emergency-interop-synthetic-v1"
MAX_MESSAGE = 65536
MAX_DICOM = 1048576
UCUM = "http://unitsofmeasure.org"
LOINC = "http://loinc.org"
CODES = {"718-7": ("Hemoglobin", "g/dL"), "2345-7": ("Glucose", "mg/dL")}
TS = "1.2.840.10008.1.2.1"
SC = "1.2.840.10008.5.1.4.1.1.7"
UID = "2.25.174369344098436458120176449251973554101"


class ContractError(ValueError):
    """Rejected input; messages never echo source payload."""


def require(condition, reason):
    if not condition:
        raise ContractError(reason)


def exact_keys(obj, keys):
    require(isinstance(obj, dict) and set(obj) == set(keys), "unexpected structure/fields")


def synthetic_observation(code="718-7", value=13.2):
    require(code in CODES, "unsupported laboratory code")
    title, unit = CODES[code]
    return {"resourceType": "Observation", "id": "synthetic-observation",
            "status": "final", "code": {"coding": [{"system": LOINC, "code": code, "display": title}]},
            "subject": {"reference": "Patient/synthetic-lab"},
            "effectiveDateTime": "2026-11-27T12:00:00Z",
            "valueQuantity": {"value": value, "unit": unit, "system": UCUM, "code": unit}}


def bundle_for(observation):
    result = {"resourceType": "Bundle", "id": "synthetic-bundle", "type": "collection",
              "meta": {"tag": [{"system": "urn:emergency:lab", "code": CONTRACT}],
                       "versionId": "1"},
              "entry": [{"resource": {"resourceType": "Patient", "id": "synthetic-lab",
                                     "active": False}},
                        {"resource": observation}]}
    validate_fhir(result, FHIR_VERSION)
    return result


def validate_fhir(bundle, version):
    """Validate this narrow local R4 contract; not a complete FHIR validator."""
    require(version == FHIR_VERSION, "unsupported FHIR version")
    require(len(json.dumps(bundle, allow_nan=False).encode("utf8")) <= MAX_MESSAGE,
            "FHIR size limit")
    exact_keys(bundle, ["resourceType", "id", "type", "meta", "entry"])
    require(bundle["resourceType"] == "Bundle" and bundle["type"] == "collection"
            and bundle["id"] == "synthetic-bundle", "only synthetic collection supported")
    require(bundle["meta"] == {"tag": [{"system": "urn:emergency:lab", "code": CONTRACT}],
                                "versionId": "1"}, "synthetic contract/version required")
    entries = bundle["entry"]
    require(isinstance(entries, list) and len(entries) == 2, "exactly two resources required")
    for entry in entries:
        exact_keys(entry, ["resource"])
    require(entries[0]["resource"] == {"resourceType": "Patient", "id": "synthetic-lab",
                                      "active": False}, "real patient fields forbidden")
    obs = entries[1]["resource"]
    exact_keys(obs, ["resourceType", "id", "status", "code", "subject",
                     "effectiveDateTime", "valueQuantity"])
    require(obs["resourceType"] == "Observation" and obs["id"] == "synthetic-observation"
            and obs["status"] == "final", "unsupported observation/status")
    require(obs["subject"] == {"reference": "Patient/synthetic-lab"}, "external subject forbidden")
    require(obs["effectiveDateTime"] == "2026-11-27T12:00:00Z", "only fixed synthetic timestamp")
    coding = obs["code"]
    exact_keys(coding, ["coding"])
    require(isinstance(coding["coding"], list) and len(coding["coding"]) == 1, "one coding required")
    c = coding["coding"][0]
    exact_keys(c, ["system", "code", "display"])
    require(c["system"] == LOINC and isinstance(c["code"], str) and c["code"] in CODES,
            "unrecognized LOINC code")
    display, unit = CODES[c["code"]]
    require(c["display"] == display, "code/display mismatch")
    quantity = obs["valueQuantity"]
    exact_keys(quantity, ["value", "unit", "system", "code"])
    require(quantity["system"] == UCUM and quantity["unit"] == unit and quantity["code"] == unit,
            "unit/code mismatch; conversions forbidden")
    value = quantity["value"]
    require(type(value) in (int, float) and math.isfinite(value) and abs(value) <= 1e9,
            "invalid numeric value")
    return copy.deepcopy(bundle)


def hl7_fixture(code="718-7", value="13.2"):
    require(code in CODES and re.fullmatch(r"-?\d{1,9}(?:\.\d{1,6})?", value),
            "unsupported numeric fixture")
    title, unit = CODES[code]
    return ("MSH|^~\\&|EMERGENCY_LAB|SYNTHETIC|EMERGENCY_LAB|SYNTHETIC|20261127120000||"
            "ORU^R01^ORU_R01|SYNTHETIC-0001|T|2.5.1\r"
            "PID|1||SYNTHETIC-LAB\r"
            "OBR|1|SYNTHETIC-ORDER|SYNTHETIC-RESULT|"+code+"^"+title+"^LN\r"
            "OBX|1|NM|"+code+"^"+title+"^LN||"+value+"|"+unit+"^"+unit+"^UCUM|||||F\r")


def hl7_to_fhir(raw):
    """One ORU_R01 result, fixed synthetic identities. No MLLP/network transport."""
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_MESSAGE, "HL7 size/type limit")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        raise ContractError("HL7 ASCII subset required") from None
    require(text.endswith("\r") and "\n" not in text and "\x0b" not in text, "ER7 CR framing required")
    parts = [segment.split("|") for segment in text[:-1].split("\r")]
    require(len(parts) == 4, "exactly MSH PID OBR OBX required")
    msh, pid, obr, obx = parts
    expected_msh = hl7_fixture().split("\r")[0].split("|")
    require(msh == expected_msh, "HL7 version/route/test processing/header mismatch")
    require(pid == ["PID", "1", "", "SYNTHETIC-LAB"], "patient identity forbidden")
    require(len(obr) == 5 and obr[:4] == ["OBR", "1", "SYNTHETIC-ORDER", "SYNTHETIC-RESULT"],
            "unsupported order")
    require(len(obx) == 12 and obx[:3] == ["OBX", "1", "NM"] and obx[4] == ""
            and obx[7:11] == ["", "", "", ""] and obx[11] == "F",
            "unsupported observation fields")
    code_parts = obx[3].split("^")
    require(len(code_parts) == 3 and code_parts[0] in CODES, "unrecognized laboratory coding")
    code = code_parts[0]; display, unit = CODES[code]
    require(code_parts == [code, display, "LN"] and obr[4] == obx[3], "order/result coding mismatch")
    require(obx[6] == unit+"^"+unit+"^UCUM", "unrecognized units; no inference")
    require(re.fullmatch(r"-?\d{1,9}(?:\.\d{1,6})?", obx[5]) is not None, "invalid NM value")
    result = bundle_for(synthetic_observation(code, float(obx[5])))
    ack = ("MSH|^~\\&|EMERGENCY_LAB|SYNTHETIC|EMERGENCY_LAB|SYNTHETIC|20261127120000||"
           "ACK^R01^ACK|SYNTHETIC-ACK-0001|T|2.5.1\rMSA|AA|SYNTHETIC-0001\r")
    return {"fhir_version": FHIR_VERSION, "source_version": HL7_VERSION,
            "source_sha256": hashlib.sha256(raw).hexdigest(), "bundle": result, "ack": ack,
            "unit_conversion_performed": False}


# The DICOM lab only accepts the exact procedural phantom generated below.
# Synthetic tags alone do NOT prove that arbitrary image pixels lack PHI.
def _element(group, element, vr, value):
    tag = struct.pack("<HH", group, element)
    if len(value) % 2:
        value += b"\0" if vr in ("UI", "OB") else b" "
    if vr == "OB":
        return tag + b"OB\0\0" + struct.pack("<I", len(value)) + value
    return tag + vr.encode("ascii") + struct.pack("<H", len(value)) + value


def dicom_fixture():
    e = _element
    text = lambda g, t, vr, s: e(g, t, vr, s.encode("ascii"))
    short = lambda g, t, n: e(g, t, "US", struct.pack("<H", n))
    meta = e(2, 1, "OB", b"\0\1") + text(2, 2, "UI", SC) + text(2, 3, "UI", UID)
    meta += text(2, 16, "UI", TS) + text(2, 18, "UI", UID+".1")
    dataset = text(8, 8, "CS", "DERIVED\\SECONDARY") + text(8, 22, "UI", SC)
    dataset += text(8, 24, "UI", UID) + text(8, 32, "DA", "20261127")
    dataset += text(8, 35, "DA", "20261127") + text(8, 48, "TM", "120000")
    dataset += text(8, 51, "TM", "120000") + text(8, 80, "SH", "")
    dataset += text(8, 96, "CS", "OT") + text(8, 100, "CS", "WSD")
    dataset += text(8, 112, "LO", "EMERGENCY SYNTHETIC LAB")
    dataset += text(8, 144, "PN", "") + text(16, 16, "PN", "SYNTHETIC^PHANTOM")
    dataset += text(16, 32, "LO", "SYNTHETIC-LAB") + text(16, 48, "DA", "")
    dataset += text(16, 64, "CS", "") + text(32, 13, "UI", UID+".2")
    dataset += text(32, 14, "UI", UID+".3") + text(32, 16, "SH", "SYNTHETIC")
    dataset += text(32, 17, "IS", "1") + text(32, 19, "IS", "1")
    dataset += short(40, 2, 1) + text(40, 4, "CS", "MONOCHROME2")
    dataset += short(40, 16, 64) + short(40, 17, 64)
    dataset += short(40, 256, 8) + short(40, 257, 8) + short(40, 258, 7)
    dataset += short(40, 259, 0) + text(40, 769, "CS", "NO")
    pixels = bytes((x*3+y*2) % 256 for y in range(64) for x in range(64))
    dataset += e(32736, 16, "OB", pixels)
    return bytes(128)+b"DICM"+e(2, 0, "UL", struct.pack("<I", len(meta)))+meta+dataset


def receive_dicom(raw):
    require(isinstance(raw, bytes) and 132 <= len(raw) <= MAX_DICOM, "DICOM size/type limit")
    require(raw[:128] == bytes(128) and raw[128:132] == b"DICM", "P10 preamble/prefix required")
    offset = 132; elements = {}
    while offset < len(raw):
        require(len(elements) < 64 and len(raw)-offset >= 8, "element/header limit")
        group, element = struct.unpack_from("<HH", raw, offset); vr = raw[offset+4:offset+6]
        require(group % 2 == 0, "private tags forbidden")
        require((group, element) not in elements, "duplicate tags forbidden")
        if vr == b"OB":
            require(len(raw)-offset >= 12 and raw[offset+6:offset+8] == b"\0\0",
                    "invalid long VR")
            length = struct.unpack_from("<I", raw, offset+8)[0]; header = 12
        else:
            require(vr in (b"UL", b"US", b"UI", b"CS", b"DA", b"TM", b"SH", b"LO", b"PN", b"IS"),
                    "unsupported VR or sequence")
            length = struct.unpack_from("<H", raw, offset+6)[0]; header = 8
        require(length != 0xffffffff and length % 2 == 0 and length <= MAX_DICOM,
                "undefined/odd/oversized element length")
        require(offset+header+length <= len(raw), "truncated element")
        elements[(group, element)] = (vr, raw[offset+header:offset+header+length])
        offset += header+length
    def val(tag): return elements.get(tag, (b"", b""))[1]
    require(val((2, 16)).rstrip(b"\0 ") == TS.encode("ascii"), "unsupported transfer syntax")
    require(val((2, 2)).rstrip(b"\0 ") == SC.encode("ascii"), "unsupported SOP class")
    require(val((40, 769)).rstrip(b" ") == b"NO", "burned-in status required")
    require(val((40, 16)) == b"@\0" and val((40, 17)) == b"@\0", "phantom dimensions required")
    require(len(val((32736, 16))) == 4096, "pixel length mismatch")
    require(hashlib.sha256(raw).digest() == hashlib.sha256(dicom_fixture()).digest(),
            "unregistered image: synthetic markers alone do not establish privacy")
    pixels = val((32736, 16))
    def chunk(kind, payload):
        return struct.pack(">I", len(payload))+kind+payload+struct.pack(">I", zlib.crc32(kind+payload))
    scanlines = b"".join(b"\0"+pixels[y*64:(y+1)*64] for y in range(64))
    png = b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR", struct.pack(">IIBBBBB",64,64,8,0,0,0,0))
    png += chunk(b"IDAT", zlib.compress(scanlines))+chunk(b"IEND", b"")
    # No metadata/string from the imported file enters HTML; no script, network or links.
    html = ('<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" '
            'content="default-src \'none\'; img-src data:; object-src \'none\'; base-uri \'none\'">'
            '<title>Synthetic image laboratory</title><h1>Synthetic phantom only</h1>'
            '<p>64 × 64; no diagnostic use; CLINICALLY_PENDING</p>'
            '<img width="512" height="512" alt="Procedural synthetic grayscale phantom" src="data:image/png;base64,'
            +base64.b64encode(png).decode("ascii")+'">')
    return {"source_sha256": hashlib.sha256(raw).hexdigest(), "rows":64,"columns":64,
            "transfer_syntax":TS,"png":png,"html":html,"patient_data":False}


def _new_file(path, data):
    with path.open("xb") as stream:
        stream.write(data)


def local_path(value):
    path = Path(value)
    require(not str(path).startswith(("\\\\", "//")), "network paths forbidden")
    components = (path, *path.parents)
    require(not any(p.is_symlink() or p.is_junction() for p in components),
            "symbolic link/junction paths forbidden")
    return path.resolve()


def read_local(value, limit):
    path = local_path(value)
    require(path.is_file(), "local regular input file required")
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "local input size limit")
    return raw


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def receive_file(kind, source, output):
    """File-based local ingress. Parse fully before creating the new output directory."""
    raw = read_local(source, MAX_DICOM if kind == "dicom" else MAX_MESSAGE)
    if kind == "dicom":
        result = receive_dicom(raw)
        outputs = {"image.png": result["png"], "viewer.html": result["html"].encode("utf8")}
    elif kind == "hl7":
        result = hl7_to_fhir(raw)
        outputs = {"bundle.json": (json.dumps(result["bundle"], indent=2)+"\n").encode("utf8"),
                   "ack.hl7": result["ack"].encode("ascii")}
    elif kind == "fhir":
        parsed = json.loads(raw, object_pairs_hook=_unique_object)
        result = validate_fhir(parsed, FHIR_VERSION)
        outputs = {"bundle.json": (json.dumps(result, indent=2)+"\n").encode("utf8")}
    else:
        raise ContractError("unsupported ingress kind")
    root = local_path(output)
    require(not root.exists(), "output directory must be new")
    root.mkdir(parents=True)
    receipt = {"contract": CONTRACT, "ingress": kind, "source_sha256": hashlib.sha256(raw).hexdigest(),
               "network_listener": False, "clinical": "CLINICALLY_PENDING",
               "files": []}
    for name, data in outputs.items():
        _new_file(root/name, data)
        receipt["files"].append({"name": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    _new_file(root/"RECEIPT.json", (json.dumps(receipt, indent=2)+"\n").encode("utf8"))
    return receipt


def demo(output):
    root = local_path(output)
    require(not root.exists(), "output directory must be new")
    root.mkdir(parents=True)
    raw = hl7_fixture().encode("ascii"); converted = hl7_to_fhir(raw)
    dcm = dicom_fixture(); rendered = receive_dicom(dcm)
    files = {"synthetic-oru.hl7":raw,
             "synthetic-bundle.json":(json.dumps(converted["bundle"],indent=2)+"\n").encode("utf8"),
             "synthetic-ack.hl7":converted["ack"].encode("ascii"),
             "synthetic-phantom.dcm":dcm,
             "synthetic-phantom.png":rendered["png"],
             "viewer.html":rendered["html"].encode("utf8")}
    for name, data in files.items(): _new_file(root/name,data)
    receipt = {"contract":CONTRACT,"base":"1f0fed8d731f65168ac338b5ddb18f451fccc6d6",
               "FHIR":FHIR_VERSION,"HL7":HL7_VERSION,"DICOM_transfer_syntax":TS,
               "synthetic_only":True,"network_listener":False,"external_connections":False,
               "unit_conversion_performed":False,"clinical":"CLINICALLY_PENDING",
               "release":"NO_GO_CLINICAL_RELEASE",
               "files":[{"name":n,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()} for n,b in files.items()]}
    _new_file(root/"RECEIPT.json",(json.dumps(receipt,indent=2)+"\n").encode("utf8"))
    return receipt


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("demo", "fhir", "hl7", "dicom"))
    parser.add_argument("output", type=Path, help="new local directory; never an existing directory")
    parser.add_argument("--input", type=Path, help="local synthetic input; required for receive modes")
    args=parser.parse_args()
    try:
        if args.mode == "demo":
            require(args.input is None, "demo does not accept input")
            result = demo(args.output)
        else:
            require(args.input is not None, "receive mode requires input")
            result = receive_file(args.mode, args.input, args.output)
        print(json.dumps(result,indent=2))
    except (ContractError, OSError, ValueError, RecursionError):
        parser.exit(2,"local interop rejected input or destination; no input content logged\n")
