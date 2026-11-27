"""Validate the dated reconciliation; never select a product or prescribe."""
import hashlib
import json
import re
from pathlib import Path


def validate(record, repository):
    repository = Path(repository)
    errors = []
    if record.get("clinical_status") != "CLINICALLY_PENDING":
        errors.append("release: CLINICALLY_PENDING required")
    if record.get("release_status") != "NO_GO_CLINICAL_RELEASE":
        errors.append("release: no clinical release authorized")
    source = repository / "docs/coordination/work-closure-20261126/SEGUIMIENTO_DECISIONES_PROPIETARIO_20261127.md"
    source_bytes = source.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != record.get("decision_source_sha256"):
        errors.append("provenance: owner decision record changed")

    product = record.get("protamine", {})
    required = {
        "product_id": "PROTAMINE_HOSPIRA_10", "jurisdiction": "ES",
        "classification": "HISTORICAL_REVOKED_ES_NOT_FOR_PRODUCT_SELECTION",
        "runtime_enabled": False, "replacement_product_id": None,
        "active_routes_changed": False, "response": "SÍ", "version": "v1",
    }
    if any(key not in product or type(product[key]) is not type(value) or product[key] != value
           for key, value in required.items()):
        errors.append("protamine: historical owner scope widened")
    if product.get("historical_rate_limit") != {
        "operator": "<", "value": 5, "unit": "mg/min", "scope": "PROTAMINE_HOSPIRA_10_ONLY",
    }:
        errors.append("protamine: historical limit changed")
    original = repository / "docs/coordination/owner-decisions-20261127/MED_RES_PROT_01_ORIGINAL_V1.md"
    if hashlib.sha256(original.read_bytes()).hexdigest() != product.get("original_fiche_sha256"):
        errors.append("protamine: original fiche changed")

    cardio = record.get("cardiovascular", [])
    if {item.get("id") for item in cardio} != {f"MED-RES-CARDIO-0{i}" for i in range(1, 7)} or len(cardio) != 6:
        errors.append("cardiovascular: six accepted identities required")
    for item in cardio:
        if item.get("response") != "SÍ" or item.get("approval_status") != "APPROVED_STRUCTURAL_SCOPE":
            errors.append("cardiovascular: recorded approval lost")
        if item.get("implementation_status") != "RECORDED_PENDING_ORIGINAL_FICHE" or item.get("original_fiche") is not None:
            errors.append("cardiovascular: original fiches not verified")
        if item.get("new_doses_authorized") is not False:
            errors.append("cardiovascular: no new doses authorized")

    cases = record.get("dermatology", {}).get("cases", [])
    source_rows = {
        row[0]: row[1:] for row in re.findall(
            r"^\| (MED-RES-DERMA-[^ |]+) \| (.*?) \| (.*?) \| (.*?) \|$",
            source_bytes.decode("utf-8"), re.M,
        )
    }
    source_ids = set(source_rows)
    if len(cases) != 23 or {item.get("id") for item in cases} != source_ids:
        errors.append("dermatology: case identities differ from decision record")
    for case in cases:
        original_case = source_rows.get(case.get("id"))
        if original_case:
            label, time, scope = original_case
            kind = "CLINICAL_REPRESENTATIVENESS_ONLY" if scope.startswith("Solo representatividad") else "CONSULTATION_DEVELOPMENT_ONLY"
            if (case.get("case"), case.get("decided_at_utc"), case.get("scope_summary"), case.get("scope_kind")) != (
                label, "2026-11-27T" + time + "Z", scope, kind,
            ):
                errors.append("dermatology: recorded case scope changed")
        if case.get("response") != "SÍ" or case.get("version") != "v1" or any(case.get(key) is not False for key in (
            "redistribution_authorized", "product_incorporation_authorized", "diagnostic_validation",
        )) or case.get("privacy_review_required") is not True:
            errors.append("dermatology: acceptance scope widened")

    design = record.get("clinical_minimal", {})
    if design.get("deployed") is not False or design.get("ux2_preserved") is not True or design.get("decision_count") != 1:
        errors.append("clinical-minimal: approval scope widened")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[2]
    record = json.loads((repository / "clinical/references/owner-decisions-2026-11-27.json").read_text(encoding="utf-8"))
    errors = validate(record, repository)
    print(json.dumps({"automated_status": "BLOCKED" if errors else "PASS", "errors": errors,
                      "clinical_status": "CLINICALLY_PENDING"}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))
