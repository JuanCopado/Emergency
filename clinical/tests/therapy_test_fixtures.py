"""Explicit API review of synthetic treatment fixtures; no bypass or mock token."""
from copy import deepcopy

from clinical_note_api import dispatch


def _suggestion_text(items):
    lines = []
    for item in items or []:
        text = item["action"]
        if item.get("rationale"):
            text += " — " + item["rationale"]
        if item.get("source_modules"):
            text += " [" + ", ".join(item["source_modules"]) + "]"
        lines.append(text)
    return "\n".join(lines)


def review_synthetic_therapy(note):
    """Create/recreate and review the exact current fixture via public API routes.

    Existing fixture treatments stay in the medication section.  The other
    synthetic text merely completes the review-contract fixture; it is not a
    newly proposed clinical regimen.  Call after every input modification when
    the test intends a successful export.  Negative privacy/type tests should
    keep their invalid input and must never invoke this helper to bless it.
    """
    old_plan = note.get("therapeutic_plan")
    if old_plan and old_plan["diagnosis"]["module_id"] is not None:
        raise AssertionError("synthetic manual fixture must not replace a canonical plan")
    previous_sections = deepcopy(old_plan["sections"]) if old_plan else None
    note.pop("therapeutic_plan", None)
    note.pop("therapeutic_review", None)
    status, draft = dispatch("/api/clinical-note/therapy/suggest", {
        "note": note,
        "selection": {"label": "Synthetic clinician-plan fixture", "module_id": None, "selection": "manual"},
        "context": {"weight_kg": None, "allergies_reviewed": True},
    })
    if status != 200 or draft["blocked"]:
        raise AssertionError({"stage": "suggest", "status": status, "issues": draft.get("issues")})
    note["therapeutic_plan"] = draft["plan"]
    assessment = note["assessment"]
    note["therapeutic_plan"]["sections"] = previous_sections or {
        "initial_actions": "Synthetic initial-action fixture, not clinical advice.",
        "medications": _suggestion_text(assessment.get("treatment_suggestions")) or "No medication is specified in this synthetic fixture.",
        "monitoring": "Synthetic monitoring fixture, not clinical advice.",
        "reassessment": _suggestion_text(assessment.get("reassessment")) or "Synthetic reassessment fixture, not clinical advice.",
        "disposition": _suggestion_text(assessment.get("disposition")) or "Synthetic disposition fixture, not clinical advice.",
    }
    status, result = dispatch("/api/clinical-note/therapy/validate", {
        "note": note,
        "confirmations": {"individualized": True, "medication_safety_reviewed": True},
    })
    if status != 200 or result["blocked"]:
        raise AssertionError({"stage": "validate", "status": status, "issues": result.get("issues")})
    note["therapeutic_review"] = result["review"]
    return note
