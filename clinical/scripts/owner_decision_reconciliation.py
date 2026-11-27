"""Validate the dated reconciliation; never select a product or prescribe."""
import hashlib
import json
import re
from pathlib import Path


def _matches_fields(item, required):
    return all(key in item and type(item[key]) is type(value) and item[key] == value
               for key, value in required.items())


def _protamine_errors(product, repository):
    errors = []
    required = {
        "id": "MED-RES-PROT-01", "decided_at_utc": "2026-11-27T06:14:21Z",
        "product_id": "PROTAMINE_HOSPIRA_10", "jurisdiction": "ES",
        "classification": "HISTORICAL_REVOKED_ES_NOT_FOR_PRODUCT_SELECTION",
        "runtime_enabled": False, "replacement_product_id": None,
        "active_routes_changed": False, "response": "SÍ", "version": "v1",
    }
    if not _matches_fields(product, required):
        errors.append("protamine: historical owner scope widened")
    if product.get("historical_rate_limit") != {
        "operator": "<", "value": 5, "unit": "mg/min", "scope": "PROTAMINE_HOSPIRA_10_ONLY",
    }:
        errors.append("protamine: historical limit changed")
    original = repository / "docs/coordination/owner-decisions-20261127/MED_RES_PROT_01_ORIGINAL_V1.md"
    if hashlib.sha256(original.read_bytes()).hexdigest() != product.get("original_fiche_sha256"):
        errors.append("protamine: original fiche changed")
    return errors


def _cardiovascular_errors(cardio, source_text):
    errors = []
    modules = {
        "MED-RES-CARDIO-01": ["arrhythmias-cardiac-arrest", "adult-arrhythmias", "pediatric-arrhythmias",
                              "adult-cardiac-arrest", "pediatric-cardiac-arrest"],
        "MED-RES-CARDIO-02": ["critical-valvular-disease"],
        "MED-RES-CARDIO-03": ["device-complications"],
        "MED-RES-CARDIO-04": ["hypertensive-emergencies"],
        "MED-RES-CARDIO-05": ["iv-antihypertensive-selection"],
        "MED-RES-CARDIO-06": ["non-coronary-chest-pain"],
    }
    summaries = dict(re.findall(r"^- (0[1-6]): (.+)$", source_text, re.M))
    if {item.get("id") for item in cardio} != set(modules) or len(cardio) != 6:
        errors.append("cardiovascular: six accepted identities required")
    for item in cardio:
        identity = item.get("id", "")
        if not _matches_fields(item, {
            "response": "SÍ", "version": "v1", "decided_at_utc": "2026-11-27T06:12:33Z",
            "approval_status": "APPROVED_STRUCTURAL_SCOPE",
            "scope_summary": summaries.get(identity[-2:]), "canonical_modules": modules.get(identity),
            "pending_kind": "EXPEDIENT_TRACEABILITY_NOT_MEDICAL_APPROVAL",
        }):
            errors.append("cardiovascular: recorded approval binding changed")
        if item.get("implementation_status") != "RECORDED_PENDING_ORIGINAL_FICHE" or item.get("original_fiche") is not None:
            errors.append("cardiovascular: original fiches not verified")
        if item.get("new_doses_authorized") is not False:
            errors.append("cardiovascular: no new doses authorized")
    return errors


def _dermatology_case_errors(case, original_case):
    errors = []
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
    return errors


def _dermatology_errors(dermatology, source_text):
    errors = []
    cases = dermatology.get("cases", [])
    if not _matches_fields(dermatology, {
        "case_count": 23, "photograph_inventory_count": 24,
        "experimental_adjudications": 0, "per_asset_file_hashes_reconciled": False,
    }):
        errors.append("dermatology: unperformed asset review or adjudication claimed")
    source_rows = {
        row[0]: row[1:] for row in re.findall(
            r"^\| (MED-RES-DERMA-[^ |]+) \| (.*?) \| (.*?) \| (.*?) \|$",
            source_text, re.M,
        )
    }
    source_ids = set(source_rows)
    if len(cases) != 23 or {item.get("id") for item in cases} != source_ids:
        errors.append("dermatology: case identities differ from decision record")
    for case in cases:
        errors.extend(_dermatology_case_errors(case, source_rows.get(case.get("id"))))

    return errors


def _review_errors(record):
    errors = []
    if not _matches_fields(record.get("clinical_minimal", {}), {
        "response": "SÍ", "scope": "VISUAL_BASE_FOR_FUTURE_INTERFACE",
        "decided_at_utc": "2026-11-27T06:37:53Z", "decision_count": 1,
        "deployed": False, "ux2_preserved": True,
    }):
        errors.append("clinical-minimal: approval scope widened")
    if not _matches_fields(record.get("independent_review", {}), {
        "reviewers_available": False, "review_status": "NOT_PERFORMED",
    }):
        errors.append("independent-review: no independent review performed for this snapshot")
    return errors


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
    source_text = source_bytes.decode("utf-8")
    errors.extend(_protamine_errors(record.get("protamine", {}), repository))
    errors.extend(_cardiovascular_errors(record.get("cardiovascular", []), source_text))
    errors.extend(_dermatology_errors(record.get("dermatology", {}), source_text))
    errors.extend(_review_errors(record))
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[2]
    record = json.loads((repository / "clinical/references/owner-decisions-2026-11-27.json").read_text(encoding="utf-8"))
    errors = validate(record, repository)
    print(json.dumps({"automated_status": "BLOCKED" if errors else "PASS", "errors": errors,
                      "clinical_status": "CLINICALLY_PENDING"}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))
