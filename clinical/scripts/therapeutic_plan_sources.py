"""Source-preserving therapeutic references, never patient-specific prescribing.

The canonical modules remain the sole clinical text.  This projection copies
whole existing paragraphs into reviewable sections and leaves unclassified or
population-ambiguous content in the complete reference.  It performs no dose
calculation, clinical ranking, or medication-safety approval.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import load_module


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_VERSION = "therapeutic-plan-sources/1.0"
SECTION_NAMES = (
    "initial_actions", "medications", "monitoring", "reassessment", "disposition",
)
SOURCE_LANGUAGE = "original"

# Explicit access to one condition inside a broad module. This is a subsection
# projection, not a new clinical module or a second copy of its recommendations.
FOCUSED_PROTOCOLS = {
    "ent-emergencies:bell-palsy": {
        "module_id": "ent-emergencies", "heading": "bell-palsy",
        "title": "Bell palsy · focused short-course reference",
    },
}

# These canonical pediatric IDs do not use the otherwise explicit prefix.
PEDIATRIC_IDS = frozenset({"croup", "bronchiolitis", "febrile-infant-0-90-days"})
# These sources are catalogues, multiple-indication umbrellas, interpretation
# frameworks or governance.  Copying their medication paragraphs together would
# create a fictitious single-case regimen.  This explicit projection policy does
# not change source evidence, owner acceptances or the canonical dosing engines.
REFERENCE_ONLY_MODULES = frozenset({
    "clinical-image-interpretation", "musculoskeletal-xray", "chest-xray",
    "pocus-image", "ecg-image", "blood-gas-image", "skin-wound-image",
    "ct-mri-screenshot", "ophthalmology-image", "other-clinical-image",
    "ecg-pocus-integration", "pocus", "clinical-note-diagnostic-support",
    "final-human-review-gate", "clinical-scores-calculators", "emergency-procedures",
    "medication-selection-safety", "pediatric-outpatient-medications",
    "pediatric-emergency-medications", "vasoactive-inotrope-infusions",
    "icu-sedation-analgesia-infusions", "iv-antihypertensive-selection",
    "empiric-antibiotics", "anticoagulation-reversal", "arrhythmias-cardiac-arrest",
    "adult-arrhythmias", "pediatric-arrhythmias", "electrolytes",
    "sodium-emergencies", "potassium-emergencies", "calcium-magnesium-emergencies",
    "acid-base-emergencies", "endocrine-metabolic", "toxicology", "pediatric-toxicology",
    "pediatric-emergencies", "pediatric-electrolyte-emergencies",
    "pediatric-hematology-oncology-emergencies", "pediatric-abdominal-surgical-emergencies",
    "pediatric-foreign-body-emergencies", "obstetric-emergencies", "geriatric-emergencies",
    "hypertensive-emergencies", "urologic-emergencies", "ophthalmology-emergencies",
    "ent-emergencies", "orthopedic-emergencies", "psychiatric-emergencies",
    "environmental-emergencies", "emergency-infectious-diseases", "hematology-oncology",
    "dermatology-severe", "soft-tissue-infections", "aki-nephrology",
    "device-complications", "syncope-falls-frailty", "non-coronary-chest-pain",
    "acute-musculoskeletal-pain", "critical-valvular-disease",
})
_PEDIATRIC = re.compile(r"\b(?:pediatric|paediatric|children|childhood|infants?|neonatal|neonates?)\b", re.I)
_ADULT = re.compile(r"\b(?:adults?|geriatric)\b", re.I)
_TOP_ITEM = re.compile(r"^(?:[-*+] |\d+[.)] )")
_HEADING = re.compile(r"^#{1,6} ")
_MEDICATION = re.compile(
    r"\b(?:dose|dosage|mg|mcg|micrograms?|milligrams?|mL|mmol|units?|IU|"
    r"bolus|infusion|corticosteroids?|predniso(?:lo)?ne|dexamethasone|hydrocortisone|"
    r"methylprednisolone|adrenaline|epinephrine|salbutamol|bronchodilat\w*|"
    r"antibiotic\w*|antimicrobial\w*|norepinephrine|insulin|anticoagula\w*)\b", re.I,
)

STANDARD_REQUIREMENTS = (
    "Individualize the reference to the confirmed indication, severity, age, weight and relevant organ function; no individualized regimen has been calculated here.",
    "Confirm medication selection, dose, route, frequency, duration, maximum and preparation through medication-selection-safety and the applicable canonical dosing module; source text is not a passed medication gate.",
    "Review allergies, concomitant medication, contraindications, monitoring and reevaluation requirements explicitly; absent information is not a negative finding.",
)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


GENERATOR_FILE_SHA256 = _sha(Path(__file__).read_bytes())


def _population(value: str) -> str:
    if value not in ("adult", "pediatric"):
        raise ValueError("population must be adult or pediatric")
    return value


def _is_pediatric_module(module_id: str) -> bool:
    return module_id.startswith("pediatric-") or module_id in PEDIATRIC_IDS


def _lead(block: str) -> str:
    """Normalize only a classifier view; returned source paragraphs stay intact."""
    line = block.splitlines()[0]
    line = re.sub(r"^(?:[-*+] |\d+[.)] |#{1,6} )", "", line)
    return line.replace("**", "").replace("`", "").strip()


def _paragraphs(body: str) -> list[str]:
    """Retain whole top-level list items, including wrapped and nested lines."""
    blocks: list[str] = []
    current: list[str] = []
    in_item = False

    def flush() -> None:
        if current:
            value = "\n".join(current).strip()
            if value:
                blocks.append(value)
            current.clear()

    for line in body.splitlines():
        if _HEADING.match(line):
            flush()
            blocks.append(line.strip())
            in_item = False
        elif _TOP_ITEM.match(line):
            flush()
            in_item = True
            current.append(line)
        elif not line.strip() and not in_item:
            flush()
        elif in_item and current and not line.strip():
            current.append(line)
        elif in_item and current and current[-1] == "" and line and not line[0].isspace():
            # A new unindented prose paragraph is not a continuation of a list.
            flush()
            in_item = False
            current.append(line)
        else:
            current.append(line)
    flush()
    return blocks


def _explicit_pediatric(block: str) -> bool:
    """A mention buried in an adult regimen is not a pediatric subsection."""
    lead = _lead(block)
    return bool(
        re.match(r"^(?:pediatric|paediatric|children|childhood|infants?|neonatal|neonates?)\b", lead, re.I)
        or (re.match(r"^Reviewed\b", lead, re.I) and _PEDIATRIC.search(lead.split(":", 1)[0]))
    )


def _scoped_blocks(blocks: list[str]) -> list[tuple[str, str | None]]:
    """Honor explicit pediatric/adult subheadings without splitting regimens."""
    headings: list[tuple[int, str | None]] = []
    scoped = []
    for block in blocks:
        if _HEADING.match(block):
            level = len(block.split(" ", 1)[0])
            while headings and headings[-1][0] >= level:
                headings.pop()
            inherited = headings[-1][1] if headings else None
            lead = _lead(block)
            if _PEDIATRIC.search(lead) and not _ADULT.search(lead):
                scope = "pediatric"
            elif _ADULT.search(lead) and not _PEDIATRIC.search(lead):
                scope = "adult"
            else:
                scope = inherited
            headings.append((level, scope))
            continue
        inherited = headings[-1][1] if headings else None
        scope = "pediatric" if _explicit_pediatric(block) else inherited
        scoped.append((block, scope))
    return scoped


def _source(module_id: str) -> tuple[str, str, str, str, str]:
    if not isinstance(module_id, str) or not module_id:
        raise ValueError("module_id must identify a canonical module")
    manifest_bytes = (ROOT / "references/module-index.md").read_bytes()
    mapping = load_module.manifest(ROOT)
    if module_id not in mapping:
        raise ValueError("unknown canonical module")
    relative = mapping[module_id]
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError("canonical module path leaves the clinical source root")
    source_bytes = path.read_bytes()
    content = source_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    marker = re.compile(rf"^## {re.escape(module_id)}\s*$", re.M)
    if len(marker.findall(content)) != 1:
        raise ValueError("expected one canonical module section")
    # Use the existing source loader, including its shared safety preamble.
    reference = load_module.load(ROOT, module_id)
    if source_bytes != path.read_bytes() or manifest_bytes != (ROOT / "references/module-index.md").read_bytes():
        raise ValueError("canonical source changed during reference generation; retry")
    body = reference.split("\n## " + module_id + "\n", 1)[1]
    return relative, reference, body, _sha(source_bytes), _sha(manifest_bytes)


def _populations(module_id: str, blocks: list[str]) -> list[str]:
    if _is_pediatric_module(module_id):
        return ["pediatric"]
    if module_id.startswith("adult-"):
        return ["adult"]
    has_separate_pediatric = any(
        scope == "pediatric" and not _ADULT.search(block)
        for block, scope in _scoped_blocks(blocks)
    )
    return ["adult", "pediatric"] if has_separate_pediatric else ["adult"]


def _focused_source(protocol_id: str):
    protocol = FOCUSED_PROTOCOLS[protocol_id]
    module_id = protocol["module_id"]
    relative, reference, body, source_sha, manifest_sha = _source(module_id)
    pattern = rf"^### {re.escape(protocol['heading'])}\n.*?(?=^### |\Z)"
    matches = list(re.finditer(pattern, body, re.M | re.S))
    if len(matches) != 1:
        raise ValueError("expected one canonical focused protocol section")
    body = matches[0].group(0).rstrip() + "\n"
    preamble = reference.split("\n## " + module_id + "\n", 1)[0]
    reference = f"{preamble}\n\n## {module_id}\n\n{body}"
    return relative, reference, body, source_sha, manifest_sha


def catalog() -> dict:
    modules = []
    mapping = load_module.manifest(ROOT)
    for module_id in mapping:
        _, _, body, _, _ = _source(module_id)
        modules.append({
            "id": module_id,
            "title": module_id.replace("-", " ").capitalize(),
            "populations": _populations(module_id, _paragraphs(body)),
            "source_language": SOURCE_LANGUAGE,
            "reference_only": module_id in REFERENCE_ONLY_MODULES,
        })
    for protocol_id, protocol in FOCUSED_PROTOCOLS.items():
        if protocol["module_id"] in mapping:
            _focused_source(protocol_id)  # fail closed if its canonical section is missing
            modules.append({
                "id": protocol_id, "title": protocol["title"],
                "populations": ["adult", "pediatric"], "source_language": SOURCE_LANGUAGE,
                "reference_only": False, "pediatric_reference_only": True,
            })
    return {"modules": modules}


def _classify(block: str) -> str | None:
    if _HEADING.match(block):
        return None
    lead = _lead(block)
    if re.match(r"^(?:reassess\w*|re-evaluat\w*|reevaluat\w*)\b", lead, re.I):
        return "reassessment"
    if re.match(r"^(?:monitor\w*|continuous monitoring|serial monitoring)\b", lead, re.I):
        return "monitoring"
    if re.match(r"^(?:disposition|discharge|before discharge|admit\w*|observation(?:/discharge)?|ICU)\b", lead, re.I):
        return "disposition"
    if _MEDICATION.search(block):
        return "medications"
    if re.match(r"^(?:initial|immediate|assess\w*|stabili[sz]\w*|ABCDE|identify|confirm|recognize|treat first|call|activate|remove|position|protect)\b", lead, re.I):
        return "initial_actions"
    if re.search(r"\b(?:reassess\w*|reevaluat\w*|re-evaluat\w*)\b", block, re.I):
        return "reassessment"
    if re.search(r"\bmonitor\w*\b", block, re.I):
        return "monitoring"
    if re.search(r"\b(?:discharge|admit|admission|disposition|transfer)\b", block, re.I):
        return "disposition"
    return None


def _revision(module_id: str | None, population: str, source_refs: list[dict], reference: str, manifest_sha256: str) -> str:
    value = {
        "generator_version": GENERATOR_VERSION,
        "generator_sha256": GENERATOR_FILE_SHA256,
        "module_id": module_id,
        "population": population,
        "source_refs": source_refs,
        "reference_sha256": _sha(reference.encode("utf-8")),
        "manifest_sha256": manifest_sha256,
    }
    return _sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def build_reference(module_id: str | None, population: str) -> dict:
    """Build an unreviewed source projection; never claim clinical completeness."""
    population = _population(population)
    sections = {name: "" for name in SECTION_NAMES}
    missing = list(STANDARD_REQUIREMENTS)
    source_refs: list[dict] = []
    reference = ""
    manifest_sha256 = _sha((ROOT / "references/module-index.md").read_bytes())

    if module_id is None:
        missing.insert(0, "No canonical module was selected; the clinician must supply and review the therapeutic plan and its sources.")
    else:
        focused = FOCUSED_PROTOCOLS.get(module_id)
        relative, reference, body, source_sha256, manifest_sha256 = (_focused_source(module_id) if focused else _source(module_id))
        blocks = _paragraphs(body)
        if not focused and population not in _populations(module_id, blocks):
            raise ValueError("canonical module has no separate therapeutic reference for the selected population")
        source_refs = [{
            "module_id": focused["module_id"] if focused else module_id,
            "path": "clinical/" + relative,
            "sha256": source_sha256,
            "language": SOURCE_LANGUAGE,
        }]
        scoped = _scoped_blocks(blocks)
        selected = [block for block, _ in scoped]
        if not _is_pediatric_module(module_id):
            if population == "pediatric":
                selected = [block for block, scope in scoped if scope == "pediatric" and not _ADULT.search(block)]
                missing.append("Only separately explicit pediatric paragraphs were prefilled from this mixed/general reference; the complete reference also contains other populations and must not be copied indiscriminately.")
            else:
                selected = [block for block, scope in scoped if scope != "pediatric" and not _PEDIATRIC.search(block)]
                if len(selected) != len(scoped):
                    missing.append("Population-mixed and pediatric paragraphs remain in the complete reference and were not prefilled as an adult regimen.")
        if focused and population == "pediatric":
            missing.append("This focused steroid regimen is prefilled only for adults aged 18 or above. Pediatric benefit is uncertain, including the 16–17 year evidence overlap; read the complete reference and make an individual clinical decision without copying the adult dose.")
        elif module_id in REFERENCE_ONLY_MODULES:
            missing.append("This source is a catalogue, broad framework or multiple-indication module. Select the concrete pathology and applicable regimen before completing the editable sections; its separate regimens have not been combined.")
        else:
            groups: dict[str, list[str]] = {name: [] for name in SECTION_NAMES}
            for block in selected:
                section = _classify(block)
                if section and block not in groups[section]:
                    groups[section].append(block)
            sections = {name: "\n\n".join(groups[name]) for name in SECTION_NAMES}
        missing.append("Section assignment is a conservative source projection, not a completeness assessment; review the entire canonical reference including its shared preamble.")

    for name, value in sections.items():
        if not value:
            missing.append(f"No separate source excerpt was identified for {name}; complete or explicitly justify this section during clinical review.")
    return {
        "reference_text": reference,
        "source_refs": source_refs,
        "sections": sections,
        "missing_requirements": missing,
        "source_revision": _revision(module_id, population, source_refs, reference, manifest_sha256),
    }
