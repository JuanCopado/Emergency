"""Reconcile the existing synthetic FHIR/HL7 contracts without interpreting results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import interop_lab as lab
import interop_phase3 as phase3


def _canonical(bundle):
    # JSON distinguishes 100 from 100.0; Python dict equality would not.
    return json.dumps(bundle, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf8")


def reconcile(fhir_raw, hl7_raw):
    """Opt-in exact-pair API; independent valid formats need not satisfy this extra contract."""
    try:
        fhir = phase3.decode_fhir(fhir_raw)
        hl7 = phase3.receive_hl7(hl7_raw)
        lab.require(_canonical(fhir) == _canonical(hl7["bundle"]),
                    "synthetic diagnostic exchange mismatch")
    except (lab.ContractError, ValueError, TypeError, KeyError, IndexError, RecursionError):
        raise lab.ContractError("synthetic diagnostic exchange rejected") from None
    return {"status": "MATCHED_SYNTHETIC_EXCHANGE", "contract": "same-synthetic-exchange-exact-v1",
            "bundle": fhir, "ack": hl7["ack"],
            "source_sha256": {"FHIR": hashlib.sha256(fhir_raw).hexdigest(),
                              "HL7": hashlib.sha256(hl7_raw).hexdigest()},
            "result_count": len(fhir["entry"])-3, "numeric_lexemes_preserved": True,
            "unit_conversion": False, "network_used": False,
            "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}


def write_receipt(fhir_path, hl7_path, output):
    # Reuse the existing no-network-path, junction, size and exclusive-write guards.
    fhir_raw = lab.read_local(fhir_path, lab.MAX_MESSAGE)
    hl7_raw = lab.read_local(hl7_path, lab.MAX_MESSAGE)
    result = reconcile(fhir_raw, hl7_raw)
    target = lab.local_path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    lab._new_file(target, (json.dumps(result, indent=2)+"\n").encode("utf8"))
    return {"status": result["status"], "result_count": result["result_count"],
            "receipt_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "clinical": result["clinical"], "release": result["release"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fhir", type=Path, required=True)
    parser.add_argument("--hl7", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new local synthetic receipt")
    args = parser.parse_args(argv)
    try:
        result = write_receipt(args.fhir, args.hl7, args.output)
    except (lab.ContractError, OSError, ValueError, RecursionError):
        parser.exit(2, "synthetic diagnostic exchange rejected; no input content logged\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
