#!/usr/bin/env python3
"""Structured clinical-note support, privacy preflight and attachment routing."""

import json
import re
import uuid
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).parents[1]
POLICY_PATH = ROOT / "qa" / "clinical-note-privacy-policy.json"

ATTACHMENT_ROUTES = {
    "ecg": ["ecg-image"],
    "chest_xray": ["chest-xray"],
    "xray_chest": ["chest-xray"],
    "musculoskeletal_xray": ["musculoskeletal-xray"],
    "ct": ["ct-mri-screenshot"],
    "ct_head": ["ct-mri-screenshot"],
    "ct_body": ["ct-mri-screenshot"],
    "mri": ["ct-mri-screenshot"],
    "ultrasound": ["pocus-image"],
    "pocus": ["pocus-image"],
    "blood_gas_image": ["blood-gas-image"],
    "skin_wound": ["skin-wound-image"],
    "ophthalmology": ["ophthalmology-image"],
    "laboratory_report": ["clinical-note-diagnostic-support", "clinical-scores-calculators"],
    "other_image": ["other-clinical-image"],
}

REPORT_SECTIONS = {
    "ecg": "ecg",
    "chest_xray": "imaging",
    "xray_chest": "imaging",
    "musculoskeletal_xray": "imaging",
    "ct": "imaging",
    "ct_head": "imaging",
    "ct_body": "imaging",
    "mri": "imaging",
    "ultrasound": "imaging",
    "pocus": "imaging",
    "blood_gas_image": "blood_gas",
    "skin_wound": "imaging",
    "ophthalmology": "imaging",
    "laboratory_report": "laboratory",
    "other_image": "other",
}

def load_policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))

def new_note(age_years=None, age_months=None, sex="unknown", language="pt-PT", privacy_mode="clinical_pseudonymized"):
    return {
        "schema_version": "1.0",
        "language": language,
        "encounter": {
            "encounter_id": str(uuid.uuid4()),
            "age": {"years": age_years, "months": age_months},
            "sex": sex,
            "origin": None,
            "transfer_status": None,
            "functional_status": None,
            "cognitive_status": None,
            "living_context": None,
        },
        "history": {
            "chief_complaint": None,
            "present_illness": None,
            "past_medical_history": [],
            "past_surgical_history": [],
            "chronic_medications": [],
            "medication_discrepancies": [],
            "allergies": [],
            "social_history": None,
            "baseline_status": None,
            "source_reliability": None,
        },
        "timeline": [],
        "exam": {
            "vitals": [],
            "general": None,
            "neurologic": None,
            "respiratory": None,
            "cardiovascular": None,
            "abdominal": None,
            "skin_wounds": None,
            "extremities": None,
            "other": None,
        },
        "complementary_tests": {
            "laboratory": [], "blood_gas": [], "ecg": [],
            "imaging": [], "microbiology": [], "other": []
        },
        "assessment": {
            "problem_representation": None,
            "active_problems": [],
            "likely_diagnoses": [],
            "differential_diagnoses": [],
            "must_not_miss": [],
            "suggested_tests": [],
            "treatment_suggestions": [],
            "disposition": [],
            "reassessment": [],
            "contradictions_to_clarify": [],
            "limitations": [],
        },
        "clinician_validation": {
            "reviewed": False, "reviewer_role": None,
            "reviewed_at": None, "changes_made": None,
        },
        "privacy": {
            "mode": privacy_mode,
            "direct_identifiers_removed": False,
            "free_text_screened": False,
            "source_metadata_checked": False,
            "burned_in_identifiers_checked": False,
            "export_allowed": False,
            "privacy_notes": [],
        },
    }

def route_attachment(kind):
    key = str(kind or "").strip().lower()
    return {
        "kind": key,
        "target_section": REPORT_SECTIONS.get(key, "other"),
        "modules": ATTACHMENT_ROUTES.get(key, ["other-clinical-image"]),
    }

def add_report(note, kind, provenance, official_report=None, ai_interpretation=None,
               findings=None, impression=None, limitations=None, source_reference=None,
               time_label=None, privacy_checked=False, burned_in_identifiers_checked=False):
    route = route_attachment(kind)
    item = {
        "kind": kind,
        "time_label": time_label,
        "provenance": provenance,
        "source_reference": source_reference,
        "official_report": official_report,
        "ai_interpretation": ai_interpretation,
        "findings": findings,
        "impression": impression,
        "limitations": limitations or [],
        "privacy_checked": bool(privacy_checked),
        "burned_in_identifiers_checked": bool(burned_in_identifiers_checked),
        "routed_modules": route["modules"],
    }
    note["complementary_tests"][route["target_section"]].append(item)
    return item

def _walk(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}", k, v
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")

def _all_text(note):
    for path, key, value in _walk(note):
        if isinstance(value, str) and value.strip():
            yield path, value

def scan_privacy(note, policy=None):
    policy = policy or load_policy()
    forbidden = {x.lower() for x in policy["forbidden_direct_identifier_fields"]}
    findings = []
    for path, key, value in _walk(note):
        if str(key).lower() in forbidden and value not in (None, "", [], {}):
            findings.append({"severity": "STOP", "code": "DIRECT_IDENTIFIER_FIELD", "path": path,
                             "message": f"Direct identifier field is not allowed: {key}"})
    compiled = []
    for rule in policy.get("free_text_flag_patterns", []):
        flags = re.I if "i" in rule.get("flags", "").lower() else 0
        compiled.append((rule["id"], re.compile(rule["pattern"], flags)))
    for path, text in _all_text(note):
        # Do not rescan the privacy policy notes themselves.
        if path.startswith("$.privacy"):
            continue
        for rid, pattern in compiled:
            if pattern.search(text):
                findings.append({"severity": "STOP", "code": "POSSIBLE_IDENTIFIER_IN_TEXT",
                                 "path": path, "pattern_id": rid,
                                 "message": f"Possible direct identifier detected in free text ({rid})."})
    return findings

def detect_data_quality_issues(note):
    issues = []
    h = note.get("history", {})
    if h.get("medication_discrepancies"):
        issues.append({"severity": "ALERT", "code": "MEDICATION_RECONCILIATION_DISCREPANCY",
                       "message": "Medication sources disagree; reconcile before treatment decisions."})
    if not isinstance(h.get("allergies"), list):
        issues.append({"severity": "ALERT", "code": "ALLERGY_STATUS_UNCLEAR",
                       "message": "Allergy status is not represented as a reviewed list."})
    for section, reports in note.get("complementary_tests", {}).items():
        for i, report in enumerate(reports):
            if report.get("ai_interpretation") and not report.get("provenance"):
                issues.append({"severity": "STOP", "code": "MISSING_PROVENANCE",
                               "message": f"{section}[{i}] AI interpretation has no provenance."})
            if report.get("ai_interpretation") and report.get("official_report") and report["ai_interpretation"] == report["official_report"]:
                issues.append({"severity": "CAUTION", "code": "AI_OFFICIAL_REPORT_COLLISION",
                               "message": f"{section}[{i}] AI interpretation duplicates official report; preserve provenance."})
    return issues

def validate_for_analysis(note):
    errors = []
    for key in ("schema_version", "encounter", "history", "exam", "complementary_tests", "assessment", "privacy"):
        if key not in note:
            errors.append({"severity": "STOP", "code": "MISSING_SECTION", "message": f"Missing note section: {key}"})
    if note.get("schema_version") != "1.0":
        errors.append({"severity": "STOP", "code": "SCHEMA_VERSION", "message": "Unsupported clinical-note schema version."})
    enc = note.get("encounter", {})
    if not enc.get("encounter_id"):
        errors.append({"severity": "STOP", "code": "ENCOUNTER_ID_REQUIRED", "message": "Pseudonymous encounter_id is required."})
    if enc.get("sex") not in {"female", "male", "intersex", "unknown"}:
        errors.append({"severity": "STOP", "code": "SEX_INVALID", "message": "Invalid sex value."})
    errors.extend(scan_privacy(note))
    errors.extend(detect_data_quality_issues(note))
    return errors

def validate_for_export(note):
    findings = validate_for_analysis(note)
    p = note.get("privacy", {})
    if not p.get("direct_identifiers_removed"):
        findings.append({"severity": "STOP", "code": "DIRECT_IDENTIFIERS_NOT_CLEARED", "message": "Direct identifiers have not been cleared."})
    if not p.get("free_text_screened"):
        findings.append({"severity": "STOP", "code": "FREE_TEXT_NOT_SCREENED", "message": "Free text has not been screened for identifiers."})
    if not note.get("clinician_validation", {}).get("reviewed"):
        findings.append({"severity": "STOP", "code": "CLINICIAN_REVIEW_REQUIRED", "message": "Clinician review is required before export."})
    if p.get("mode") == "external_anonymized" and not p.get("source_metadata_checked"):
        findings.append({"severity": "STOP", "code": "SOURCE_METADATA_NOT_CHECKED", "message": "Source metadata must be checked for external anonymized export."})
    has_embedded_image_interpretation = any(
        r.get("ai_interpretation")
        for reports in note.get("complementary_tests", {}).values()
        for r in reports
        if isinstance(r, dict)
    )
    if p.get("mode") == "external_anonymized" and has_embedded_image_interpretation and not p.get("burned_in_identifiers_checked"):
        findings.append({"severity": "STOP", "code": "BURNED_IN_IDENTIFIERS_NOT_CHECKED",
                         "message": "Burned-in identifiers must be checked for external export of image-derived content."})
    blocked = any(x["severity"] == "STOP" for x in findings)
    return {"blocked": blocked, "findings": findings, "export_allowed": not blocked}

def diagnostic_support_contract(note):
    """Return the privacy-safe structured context expected by the reasoning layer."""
    issues = validate_for_analysis(note)
    if any(x["severity"] == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "context": None}
    context = deepcopy(note)
    context.pop("privacy", None)
    context.pop("clinician_validation", None)
    return {
        "blocked": False,
        "issues": issues,
        "context": context,
        "required_output": {
            "problem_representation": "concise synthesis",
            "likely_diagnoses": "ranked qualitative confidence high/moderate/low",
            "differential_diagnoses": "alternatives with evidence for/against",
            "must_not_miss": "time-critical alternatives",
            "suggested_tests": "only tests that discriminate or change management",
            "treatment_suggestions": "stabilization then syndrome-specific treatment",
            "disposition": "admit/observe/discharge/escalate with rationale",
            "reassessment": "what to recheck and when",
            "limitations": "missing data and uncertainty",
        },
    }
