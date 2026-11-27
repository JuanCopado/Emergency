"""Closed synthetic R4/HL7 and in-memory PACS laboratory; no network transport."""
from __future__ import annotations

import argparse
import copy
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

import interop_lab as lab
import interop_phase2 as phase2

CONTRACT = "emergency-interop-synthetic-v3"
SPECIMEN = {"resourceType": "Specimen", "id": "synthetic-specimen", "status": "available",
            "subject": {"reference": "Patient/synthetic-lab"}}
SPECIMEN_REF = {"reference": "Specimen/synthetic-specimen"}
ROLES = {"reviewer": frozenset({"fhir", "hl7", "pacs-read", "audit"}),
         "technician": frozenset({"fhir", "hl7", "pacs-store", "pacs-read", "audit"})}
ERROR_CODES = frozenset({"invalid", "forbidden", "not-found", "expired", "throttled"})
POLICY = {"data": "registered-synthetic-only", "session_max_seconds": 120,
          "pacs_ttl_seconds": 30, "audit_ttl_seconds": 60, "audit_max_events": 32,
          "session_max_attempts": 40, "pacs_max_instances": 1,
          "authentication": "ephemeral local harness credential; not institutional identity",
          "network": "none", "hospital_transport": "always-deny",
          "secure_erasure_guaranteed": False, "clinical": "CLINICALLY_PENDING",
          "release": "NO_GO_CLINICAL_RELEASE"}


def outcome(code):
    """Fixed, non-reflective R4 OperationOutcome for technical exchange errors."""
    lab.require(code in ERROR_CODES, "unsupported outcome code")
    return {"resourceType": "OperationOutcome", "issue": [{"severity": "error", "code": code}]}


def with_specimen(bundle):
    checked = phase2.validate_bundle(bundle, lab.FHIR_VERSION)
    checked["id"] = "synthetic-specimen-report-bundle"
    checked["meta"]["tag"][0]["code"] = CONTRACT
    for entry in checked["entry"][1:]:
        resource = entry["resource"]
        resource["specimen"] = ([copy.deepcopy(SPECIMEN_REF)]
                                if resource["resourceType"] == "DiagnosticReport"
                                else copy.deepcopy(SPECIMEN_REF))
    checked["entry"].insert(1, {"resource": copy.deepcopy(SPECIMEN)})
    return checked


def validate_bundle(bundle, version=lab.FHIR_VERSION):
    """Exact closed local R4 subset, not a general FHIR profile validator."""
    lab.require(version == lab.FHIR_VERSION, "unsupported FHIR version")
    lab.require(isinstance(bundle, dict), "bundle object required")
    lab.require(len(json.dumps(bundle, allow_nan=False).encode("utf8")) <= lab.MAX_MESSAGE,
                "FHIR size limit")
    base = copy.deepcopy(bundle)
    lab.exact_keys(base, ["resourceType", "id", "type", "meta", "entry"])
    lab.require(base["id"] == "synthetic-specimen-report-bundle", "synthetic identity required")
    lab.require(base["meta"] == {"versionId": "1", "tag": [
        {"system": "urn:emergency:lab", "code": CONTRACT}]}, "contract/version mismatch")
    entries = base["entry"]
    lab.require(isinstance(entries, list) and 4 <= len(entries) <= 5,
                "patient, specimen, one or two observations and report required")
    for entry in entries:
        lab.exact_keys(entry, ["resource"])
        lab.require(isinstance(entry["resource"], dict), "resource object required")
    lab.require(entries[1]["resource"] == SPECIMEN, "specimen identity/subject/fields mismatch")
    entries.pop(1)
    for entry in entries[1:]:
        resource = entry["resource"]
        expected = ([SPECIMEN_REF] if resource.get("resourceType") == "DiagnosticReport"
                    else SPECIMEN_REF)
        lab.require(resource.pop("specimen", None) == expected, "specimen reference mismatch")
    base["id"] = "synthetic-report-bundle"
    base["meta"]["tag"][0]["code"] = phase2.CONTRACT
    phase2.validate_bundle(base, version)
    return copy.deepcopy(bundle)


def decode_fhir(raw):
    lab.require(isinstance(raw, bytes) and 0 < len(raw) <= lab.MAX_MESSAGE, "FHIR size/type limit")
    parsed = json.loads(raw, object_pairs_hook=lab._unique_object,
                        parse_int=lab.lossless_number, parse_float=lab.lossless_number)
    return validate_bundle(parsed)


def receive_hl7(raw):
    """Support the two already documented ORU_R01 shapes, never general HL7 ingestion."""
    lab.require(isinstance(raw, bytes) and 0 < len(raw) <= lab.MAX_MESSAGE, "HL7 size/type limit")
    header = raw.split(b"\r", 1)[0]
    single = lab.hl7_fixture().split("\r", 1)[0].encode("ascii")
    if header == single:
        converted = lab.hl7_to_fhir(raw)
        observations = [converted["bundle"]["entry"][1]["resource"]]
        bundle = phase2.bundle_for_results(observations)
    else:
        converted = phase2.hl7_panel_to_fhir(raw)
        bundle = converted["bundle"]
    return {"bundle": with_specimen(bundle), "ack": converted["ack"],
            "source_sha256": hashlib.sha256(raw).hexdigest(), "unit_conversion": False}


class SyntheticGateway:
    """Trusted, single-process lab only. Token issuance never authenticates a human."""

    def __init__(self, *, clock=time.monotonic):
        self._clock = clock
        self._session = None
        self._instance = None
        self._events = []
        self._sequence = 0
        self._closed = False

    def _purge(self):
        now = self._clock()
        if self._session is not None and now >= self._session["deadline"]:
            self._session = None
            self._instance = None
        if self._instance is not None and now >= self._instance["deadline"]:
            self._instance = None
        self._events = [e for e in self._events if now-e["time"] < POLICY["audit_ttl_seconds"]]

    def _record(self, operation, result):
        self._sequence += 1
        self._events.append({"sequence": self._sequence, "time": self._clock(),
                             "operation": operation, "result": result})
        self._events = self._events[-POLICY["audit_max_events"]:]

    def issue_lab_credential(self, role, *, seconds=60):
        lab.require(not self._closed and isinstance(role, str) and role in ROLES,
                    "invalid lab role or closed gateway")
        lab.require(type(seconds) is int and 1 <= seconds <= POLICY["session_max_seconds"],
                    "invalid credential lifetime")
        self._purge()
        token = secrets.token_hex(32)
        self._session = {"digest": hashlib.sha256(token.encode("ascii")).digest(),
                         "permissions": ROLES[role], "deadline": self._clock()+seconds,
                         "attempts": 0}
        # Rotation revokes old credentials and clears the previous session's payload.
        self._instance = None
        self._record("session", "issued")
        return token

    def _authorized(self, operation, token):
        self._purge()
        if self._closed or self._session is None:
            return "expired"
        self._session["attempts"] = min(self._session["attempts"]+1,
                                        POLICY["session_max_attempts"]+1)
        if self._session["attempts"] > POLICY["session_max_attempts"]:
            return "throttled"
        valid = (isinstance(token, str) and len(token) == 64 and token.isascii()
                 and hmac.compare_digest(self._session["digest"],
                                         hashlib.sha256(token.encode("ascii")).digest()))
        if not valid or operation not in self._session["permissions"]:
            return "forbidden"
        return None

    def exchange(self, operation, token, payload=b""):
        # Operation strings from callers must never enter audit/error output.
        if not isinstance(operation, str) or operation not in {
                "fhir", "hl7", "pacs-store", "pacs-read", "audit"}:
            self._purge()
            self._record("unsupported", "forbidden")
            return outcome("forbidden")
        error = self._authorized(operation, token)
        if error is not None:
            self._record(operation, error)
            return outcome(error)
        try:
            result = self._perform(operation, payload)
        except (lab.ContractError, ValueError, TypeError, KeyError, IndexError, RecursionError):
            self._record(operation, "invalid")
            return outcome("invalid")
        status = (result["issue"][0]["code"]
                  if result.get("resourceType") == "OperationOutcome" else "success")
        self._record(operation, status)
        return result

    def _perform(self, operation, payload):
        if operation == "fhir":
            return decode_fhir(payload)
        if operation == "hl7":
            return receive_hl7(payload)
        if operation == "pacs-store":
            rendered = phase2.secure_view(payload)
            self._instance = {"raw": payload, "deadline": self._clock()+POLICY["pacs_ttl_seconds"]}
            return {"instance": lab.UID, "source_sha256": rendered["source_sha256"],
                    "stored": True, "transport": "local-memory"}
        lab.require(payload == b"", "unexpected operation payload")
        if operation == "audit":
            return {"events": copy.deepcopy(self._events), "payloads_logged": False,
                    "durable": False, "tamper_resistant": False}
        if self._instance is None:
            return outcome("not-found")
        return phase2.secure_view(self._instance["raw"])

    def retention_status(self):
        """Harness inspection contains only counts; sweep is lazy, not a background timer."""
        self._purge()
        return {"instances": int(self._instance is not None), "events": len(self._events),
                "session_active": self._session is not None,
                "cleanup": "on-operation-or-explicit-sweep; no secure erasure guarantee"}

    def connect_operational(self, _request):
        raise lab.ContractError("hospital transport disabled")

    def close(self):
        self._session = None
        self._instance = None
        self._events = []
        self._closed = True


def demo(output):
    root = lab.local_path(output)
    lab.require(not root.exists(), "output directory must be new")
    session = SyntheticGateway()
    token = session.issue_lab_credential("technician")
    result = session.exchange("hl7", token, phase2.hl7_panel_fixture().encode("ascii"))
    fhir_raw = (json.dumps(result["bundle"], indent=2)+"\n").encode("utf8")
    lab.require(session.exchange("fhir", token, fhir_raw) == result["bundle"], "roundtrip failed")
    store = session.exchange("pacs-store", token, lab.dicom_fixture())
    view = session.exchange("pacs-read", token)
    rejected = session.exchange("hl7", token, b"invalid synthetic test")
    audit = session.exchange("audit", token)
    session.close()
    root.mkdir(parents=True)
    outputs = {"bundle.json": fhir_raw, "ack.hl7": result["ack"].encode("ascii"),
               "pacs-receipt.json": json.dumps(store, indent=2).encode("utf8"),
               "viewer.html": view["html"].encode("utf8"), "image.png": view["png"],
               "rejected-outcome.json": json.dumps(rejected).encode("utf8"),
               "audit.json": json.dumps(audit, indent=2).encode("utf8"),
               "POLICY.json": json.dumps(POLICY, indent=2).encode("utf8")}
    records = []
    for name, raw in outputs.items():
        lab._new_file(root/name, raw)
        records.append({"name": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    receipt = {"contract": CONTRACT, "base": "f32d211eed6a7baa7c42aadae583f6726e9e7e9b",
               "synthetic_only": True, "network_used": False, "credentials_exported": False,
               "session_closed": True, "visual": "NOT_EXECUTED_POLICY_BLOCKED",
               "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE", "files": records}
    lab._new_file(root/"RECEIPT.json", (json.dumps(receipt, indent=2)+"\n").encode("utf8"))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new local synthetic demonstration directory")
    args = parser.parse_args()
    try:
        print(json.dumps(demo(args.output), indent=2))
    except (lab.ContractError, OSError, ValueError, RecursionError):
        parser.exit(2, "synthetic phase-three exchange rejected; no input content logged\n")
