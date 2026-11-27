"""Source-bound therapeutic drafts and explicit review of an exact note version.

No prescribing model or duplicate dose calculator lives here. Canonical reference
paragraphs are a draft; a physician must individualize them and review medication
safety. A signed receipt records that action and integrity, not professional
identity, autonomous medication clearance, or global clinical validation.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import secrets
import uuid

from clinical_note_support import validate_for_analysis, validate_contract
from therapeutic_plan_sources import build_reference

SECTION_KEYS = ("initial_actions", "medications", "monitoring", "reassessment", "disposition")
REVIEW_SCOPE = "physician_review_of_this_version"
_KEY = (os.environ.get("CLINICAL_NOTE_THERAPY_HMAC_KEY") or "").encode() or secrets.token_bytes(32)

# Error text is static: never echo a rejected clinical field into an HTTP error.
MESSAGES = {
    "THERAPY_AGE_REQUIRED": ("Indica la edad en años o meses para elegir adulto o pediatría.", "Indique a idade em anos ou meses para selecionar adulto ou pediatria.", "Enter age in years or months to select adult or pediatric care.", "请输入年龄（岁或月龄），以选择成人或儿科路径。"),
    "THERAPY_AGE_AMBIGUOUS": ("Utiliza años o meses, no ambos; la edad debe ser válida.", "Utilize anos ou meses, não ambos; a idade deve ser válida.", "Use years or months, not both; age must be valid.", "请使用岁或月龄，不能同时填写；年龄必须有效。"),
    "THERAPY_SELECTION_INVALID": ("Selecciona una patología y un módulo compatible, o completa una pauta manual.", "Selecione uma patologia e um módulo compatível, ou complete um plano manual.", "Select a condition and a compatible module, or complete a manual plan.", "请选择疾病及适用模块，或填写手工治疗方案。"),
    "THERAPY_CONTEXT_INVALID": ("Comprueba el peso y la revisión explícita de alergias.", "Verifique o peso e a revisão explícita de alergias.", "Check the weight and explicit allergy review.", "请检查体重并明确确认过敏史已复核。"),
    "THERAPY_REQUIRED": ("La salida de tratamiento requiere una pauta y su validación médica vigente.", "A exportação de tratamento requer um plano e validação médica atual.", "Treatment export requires a plan with a current physician review.", "导出治疗内容需要治疗方案及有效的医生复核。"),
    "THERAPY_DRAFT_INVALID": ("La propuesta no es íntegra o pertenece a otra sesión; vuelve a generarla.", "A proposta não está íntegra ou pertence a outra sessão; gere-a novamente.", "The draft is not intact or belongs to another session; generate it again.", "草案完整性校验失败或属于其他会话，请重新生成。"),
    "THERAPY_CONTEXT_CHANGED": ("El caso o idioma ha cambiado desde la propuesta; regenera la pauta.", "O caso ou idioma mudou desde a proposta; gere novamente o plano.", "The case or language changed after generation; regenerate the plan.", "生成后病例或语言已更改，请重新生成方案。"),
    "THERAPY_SOURCE_CHANGED": ("La referencia ha cambiado; regenera la pauta antes de validarla.", "A referência mudou; gere novamente o plano antes de validar.", "The reference changed; regenerate the plan before review.", "参考内容已更改，请在复核前重新生成方案。"),
    "THERAPY_SECTIONS_INCOMPLETE": ("Completa las cinco secciones; documenta cuando una intervención no esté indicada.", "Complete as cinco secções; documente quando uma intervenção não está indicada.", "Complete all five sections; document when an intervention is not indicated.", "请填写全部五部分；如某项干预无指征，请注明。"),
    "THERAPY_ALLERGY_REVIEW_REQUIRED": ("Revisa las alergias y documenta la incertidumbre antes de validar.", "Reveja as alergias e documente a incerteza antes de validar.", "Review allergies and document uncertainty before validation.", "复核前请核实过敏史，并记录不确定信息。"),
    "THERAPY_WEIGHT_REQUIRED": ("La pauta depende del peso; aporta el peso verificado y regenera la propuesta.", "O plano depende do peso; introduza o peso verificado e gere novamente a proposta.", "The plan uses weight-based dosing; enter verified weight and regenerate the draft.", "方案包含按体重给药；请填写核实后的体重并重新生成。"),
    "THERAPY_SURFACE_DOSE_UNRESOLVED": ("La pauta expresa dosis por superficie corporal: individualiza la dosis absoluta con el cálculo revisado antes de validarla.", "O plano expressa doses por superfície corporal: individualize a dose absoluta com o cálculo revisto antes de validar.", "The plan expresses body-surface-area dosing: individualize the absolute dose using the reviewed calculation before validation.", "方案包含按体表面积给药，请根据已复核的计算填写个体化绝对剂量后再验证。"),
    "THERAPY_CONFIRMATIONS_REQUIRED": ("Confirma la individualización completa y la revisión de seguridad farmacológica.", "Confirme a individualização completa e a revisão de segurança farmacológica.", "Confirm complete individualization and medication safety review.", "请确认已完成个体化调整及用药安全复核。"),
    "THERAPY_REVIEW_INVALID": ("La validación no corresponde a esta versión; revisa y valida de nuevo.", "A validação não corresponde a esta versão; reveja e valide novamente.", "The review does not match this version; review and validate again.", "复核与当前版本不符，请重新检查并验证。"),
    "THERAPY_PRIVACY_REQUIRED": ("Confirma la revisión de privacidad antes de validar la pauta.", "Confirme a revisão de privacidade antes de validar o plano.", "Confirm privacy review before validating the plan.", "验证方案前请确认隐私复核。"),
}


def _issue(note, code, **extra):
    position = {"es-ES": 0, "pt-PT": 1, "en": 2, "zh": 3}.get(note.get("language"), 2)
    return {"severity": "STOP", "code": code, "message": MESSAGES[code][position], **extra}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _digest(value):
    return hashlib.sha256(_json(value)).hexdigest()


def _sign(domain, value):
    revision = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return hmac.new(_KEY, domain.encode() + b"\0" + revision.encode() + b"\0" + _json(value), hashlib.sha256).hexdigest()


def _valid_signature(token, expected):
    return isinstance(token, str) and re.fullmatch(r"[0-9a-f]{64}", token) is not None and hmac.compare_digest(token, expected)


def context_digest(note):
    context = deepcopy(note)
    for key in ("therapeutic_plan", "therapeutic_review", "clinician_validation"):
        context.pop(key, None)
    context.get("privacy", {}).pop("export_allowed", None)
    # This former output is replaced by the selected, reviewed plan. All other
    # clinical content, including the selected diagnoses and language, stays bound.
    for key in ("treatment_suggestions", "disposition", "reassessment"):
        context.get("assessment", {}).pop(key, None)
    return _digest(context)


def _population(note):
    age = note.get("encounter", {}).get("age", {})
    years, months = age.get("years"), age.get("months")
    if years is None and months is None:
        return None, [_issue(note, "THERAPY_AGE_REQUIRED")]
    if years is not None and months is not None:
        return None, [_issue(note, "THERAPY_AGE_AMBIGUOUS")]
    value = years if years is not None else months
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or value > (130 if years is not None else 1560):
        return None, [_issue(note, "THERAPY_AGE_AMBIGUOUS")]
    return ("adult" if (value if years is not None else value / 12) >= 18 else "pediatric"), []


def _metadata(plan):
    return {key: value for key, value in plan.items() if key not in {"sections", "generation_token"}}


def trusted_source_paths(note):
    """Public source text is not patient-entered text.

    Exempt only an exact canonical string after authenticating its generation
    metadata and reloading the current source. A single edit removes the section
    exemption; fields with a pathology label, clinical inputs or physician edits
    always remain subject to the existing privacy detector.
    """
    plan = note.get("therapeutic_plan")
    if not isinstance(plan, dict) or validate_contract(plan, {"$ref": "#/$defs/therapeutic_plan"}):
        return set()
    if not _valid_signature(plan["generation_token"], _sign("therapy-draft-v1", _metadata(plan))):
        return set()
    try:
        reference = build_reference(plan["diagnosis"]["module_id"], plan["population"])
    except (KeyError, ValueError, OSError, RuntimeError):
        return set()
    if any(plan[key] != reference[key] for key in ("reference_text", "source_refs", "source_revision", "missing_requirements")):
        return set()
    paths = {("therapeutic_plan", "reference_text")}
    paths.update(("therapeutic_plan", "missing_requirements", index) for index in range(len(reference["missing_requirements"])))
    paths.update(("therapeutic_plan", "sections", key) for key in SECTION_KEYS if plan["sections"][key] == reference["sections"][key])
    return paths


def suggest(payload):
    note = payload.get("note") or {}
    issues = validate_for_analysis(note)
    if any(x.get("severity") == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "plan": None}
    population, age_issues = _population(note)
    issues.extend(age_issues)
    selection = payload.get("selection")
    context = payload.get("context")
    if not isinstance(selection, dict) or set(selection) != {"label", "module_id", "selection"} or not isinstance(selection.get("label"), str) or not 0 < len(selection["label"].strip()) <= 200 or selection.get("selection") not in {"diagnostic", "manual"} or not (selection.get("module_id") is None or isinstance(selection.get("module_id"), str)):
        issues.append(_issue(note, "THERAPY_SELECTION_INVALID"))
    if not isinstance(context, dict) or set(context) != {"weight_kg", "allergies_reviewed"} or type(context.get("allergies_reviewed")) is not bool:
        issues.append(_issue(note, "THERAPY_CONTEXT_INVALID"))
    elif context["weight_kg"] is not None and (type(context["weight_kg"]) not in (int, float) or not math.isfinite(context["weight_kg"]) or not 0 < context["weight_kg"] <= 1000):
        issues.append(_issue(note, "THERAPY_CONTEXT_INVALID"))
    if any(x.get("severity") == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "plan": None}
    if selection["selection"] == "diagnostic":
        candidates = note["assessment"].get("likely_diagnoses", []) + note["assessment"].get("differential_diagnoses", []) + note["assessment"].get("must_not_miss", [])
        if not any(x.get("diagnosis") == selection["label"] and selection["module_id"] in x.get("source_modules", []) for x in candidates):
            return {"blocked": True, "issues": [_issue(note, "THERAPY_SELECTION_INVALID")], "plan": None}
    try:
        reference = build_reference(selection["module_id"], population)
    except (KeyError, ValueError, RuntimeError):
        return {"blocked": True, "issues": [_issue(note, "THERAPY_SELECTION_INVALID")], "plan": None}
    plan = {
        "schema_version": "1.0", "plan_id": str(uuid.uuid4()),
        "diagnosis": deepcopy(selection), "population": population, "context": deepcopy(context),
        **reference, "generated_from_digest": context_digest(note),
        "suggested_content_digest": _digest(reference["sections"]),
        "medication_safety": {"status": "REVIEW_REQUIRED", "actionable": False, "required_module": "medication-selection-safety"},
    }
    plan["generation_token"] = _sign("therapy-draft-v1", _metadata(plan))
    proposed = deepcopy(note)
    proposed["therapeutic_plan"] = plan
    proposed.pop("therapeutic_review", None)
    # Includes the manual pathology label and every newly included source paragraph.
    new_issues = validate_for_analysis(proposed)
    if any(x.get("severity") == "STOP" for x in new_issues):
        return {"blocked": True, "issues": new_issues, "plan": None}
    return {"blocked": False, "issues": issues, "plan": plan}


def _check_draft(note):
    issues = []
    plan = note.get("therapeutic_plan")
    if not isinstance(plan, dict):
        return [_issue(note, "THERAPY_REQUIRED")]
    if validate_contract(plan, {"$ref": "#/$defs/therapeutic_plan"}):
        return [_issue(note, "THERAPY_DRAFT_INVALID")]
    token = plan.get("generation_token", "")
    if not _valid_signature(token, _sign("therapy-draft-v1", _metadata(plan))):
        return [_issue(note, "THERAPY_DRAFT_INVALID")]
    if context_digest(note) != plan["generated_from_digest"]:
        issues.append(_issue(note, "THERAPY_CONTEXT_CHANGED"))
    try:
        reference = build_reference(plan["diagnosis"]["module_id"], plan["population"])
        if any(plan[key] != reference[key] for key in ("source_revision", "source_refs", "reference_text")):
            issues.append(_issue(note, "THERAPY_SOURCE_CHANGED"))
    except (ValueError, KeyError, OSError, RuntimeError):
        issues.append(_issue(note, "THERAPY_SOURCE_CHANGED"))
    return issues


def _completion_issues(note):
    plan = note["therapeutic_plan"]
    sections = plan["sections"]
    issues = []
    missing = [key for key in SECTION_KEYS if not sections[key].strip() or len(sections[key]) > 50000]
    if missing:
        issues.append(_issue(note, "THERAPY_SECTIONS_INCOMPLETE", sections=missing))
    if plan["context"]["allergies_reviewed"] is not True:
        issues.append(_issue(note, "THERAPY_ALLERGY_REVIEW_REQUIRED"))
    clinical_text = "\n".join(sections.values())
    if re.search(r"(?:/\s*kg\b|\b(?:per|por)\s+kg\b|\bkg\s*(?:[⁻−-]\s*[¹1]|\^\s*-\s*1))", clinical_text, re.I) and plan["context"]["weight_kg"] is None:
        issues.append(_issue(note, "THERAPY_WEIGHT_REQUIRED"))
    # This workflow has no BSA calculator or structured BSA input. Do not give a
    # formula-only order a completed-review state in lieu of an absolute regimen.
    if re.search(r"(?:/\s*m(?:[²2]|\^\s*2)|\b(?:per|por)\s+m(?:[²2]|\^\s*2)|\bm\s*(?:[⁻−-]\s*[²2]|\^\s*-\s*2))", clinical_text, re.I):
        issues.append(_issue(note, "THERAPY_SURFACE_DOSE_UNRESOLVED"))
    return issues


def validate(payload):
    note = payload.get("note") or {}
    issues = validate_for_analysis(note)
    if any(x.get("severity") == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "review": None}
    issues.extend(_check_draft(note))
    if any(x.get("severity") == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "review": None}
    issues.extend(_completion_issues(note))
    confirmations = payload.get("confirmations")
    if not isinstance(confirmations, dict) or set(confirmations) != {"individualized", "medication_safety_reviewed"} or any(value is not True for value in confirmations.values()):
        issues.append(_issue(note, "THERAPY_CONFIRMATIONS_REQUIRED"))
    if any(note["privacy"].get(key) is not True for key in ("direct_identifiers_removed", "free_text_screened")):
        issues.append(_issue(note, "THERAPY_PRIVACY_REQUIRED"))
    if any(x.get("severity") == "STOP" for x in issues):
        return {"blocked": True, "issues": issues, "review": None}
    plan = note["therapeutic_plan"]
    review = {
        "status": "validated", "scope": REVIEW_SCOPE,
        "mode": "as_suggested" if _digest(plan["sections"]) == plan["suggested_content_digest"] else "edited",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "plan_digest": _digest(plan), "context_digest": context_digest(note),
        "confirmations": deepcopy(confirmations),
    }
    review["validation_token"] = _sign("therapy-physician-review-v1", review)
    return {"blocked": False, "issues": issues, "review": review}


def export_findings(note):
    """Called by the common exporter, including direct PDF/DOCX/JSON entry points."""
    plan = note.get("therapeutic_plan")
    if not plan:
        if note.get("therapeutic_review") or note.get("assessment", {}).get("treatment_suggestions"):
            return [_issue(note, "THERAPY_REQUIRED")]
        return []
    issues = _check_draft(note)
    if issues:
        return issues
    issues.extend(_completion_issues(note))
    review = note.get("therapeutic_review")
    if not isinstance(review, dict) or validate_contract(review, {"$ref": "#/$defs/therapeutic_review"}):
        return issues + [_issue(note, "THERAPY_REVIEW_INVALID")]
    signed = {key: value for key, value in review.items() if key != "validation_token"}
    if (not _valid_signature(review["validation_token"], _sign("therapy-physician-review-v1", signed))
            or review["plan_digest"] != _digest(plan)
            or review["context_digest"] != context_digest(note)
            or any(value is not True for value in review["confirmations"].values())):
        issues.append(_issue(note, "THERAPY_REVIEW_INVALID"))
    return issues


def export_payload(note):
    """Keep one therapeutic plan in JSON; replaced legacy outputs are not signed."""
    result = deepcopy(note)
    if result.get("therapeutic_plan"):
        for key in ("treatment_suggestions", "disposition", "reassessment"):
            result["assessment"][key] = []
    return result


def export_sections(note):
    """Render the same single plan in all document formats, with its provenance."""
    plan, review = note["therapeutic_plan"], note["therapeutic_review"]
    position = {"es-ES": 0, "pt-PT": 1, "en": 2, "zh": 3}.get(note.get("language"), 2)
    words = [
        ("Pauta terapéutica revisada por el médico", "Plano terapêutico revisto pelo médico", "Physician-reviewed therapeutic plan", "医生已复核的治疗方案"),
        ("Medidas iniciales y no farmacológicas", "Medidas iniciais e não farmacológicas", "Initial and non-drug measures", "初始措施与非药物治疗"),
        ("Tratamiento farmacológico", "Tratamento farmacológico", "Medication plan", "药物治疗方案"),
        ("Monitorización y seguridad", "Monitorização e segurança", "Monitoring and safety", "监测与安全"),
        ("Reevaluación y criterios de escalada", "Reavaliação e critérios de escalada", "Reassessment and escalation", "复评与升级标准"),
        ("Destino y seguimiento", "Destino e seguimento", "Disposition and follow-up", "去向与随访"),
        ("Trazabilidad de la pauta", "Rastreabilidade do plano", "Plan traceability", "方案溯源"),
    ]
    labels = [word[position] for word in words]
    sections = [(labels[0], [plan["diagnosis"]["label"], f'{plan["population"]} | {review["reviewed_at"]} | {review["mode"]}'])]
    sections.extend((labels[index + 1], [plan["sections"][key]]) for index, key in enumerate(SECTION_KEYS))
    scope = (
        "La revisión médica corresponde a esta versión. No constituye autorización farmacológica automática ni validación clínica global. Referencias canónicas en su idioma original.",
        "A revisão médica corresponde a esta versão. Não constitui autorização farmacológica automática nem validação clínica global. Referências canónicas no idioma original.",
        "Physician review applies to this version. It is not automated medication clearance or global clinical validation. Canonical references remain in their original language.",
        "医生复核仅适用于此版本，并不代表自动用药许可或整体临床验证。规范参考内容保留原始语言。",
    )[position]
    source_lines = [f'{source["module_id"]} | {source["path"]} | SHA-256 {source["sha256"]}' for source in plan["source_refs"]]
    sections.append((labels[6], [scope, f'Plan: {plan["plan_id"]}', f'SHA-256: {review["plan_digest"]}', f'Source revision: {plan["source_revision"]}', *source_lines]))
    return sections
