#!/usr/bin/env python3
"""Audit how much of the v1.41 textual procedure library is ready for canonical JSON migration.

This script is deliberately fail-closed. It does not invent missing clinical fields and
does not promote any procedure. It only maps what is explicitly present in the family
Markdown files and reports gaps against the canonical schema.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "modules" / "procedures"
OUT = ROOT / "qa" / "procedure-schema-coverage-v1.41.json"

HEADER = re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})\s+—\s+(.+?)(?:\s+—\s+([A-Z/]+))?$", re.M)

FIELD_PATTERNS = {
    "objective": [r"\*\*Objetivo:\*\*", r"\*\*Uso:\*\*"],
    "indications": [r"\*\*Indicaciones?:\*\*", r"\bIndicación\b"],
    "contraindications_precautions": [r"\*\*Contraindicaciones?", r"\*\*Precauciones?", r"\bprecauc"],
    "equipment": [r"\*\*Material", r"\bequipo\b"],
    "anatomy": [r"\*\*Anatom", r"\blandmark", r"\breferencias anat"],
    "preparation": [r"\*\*Preparación", r"\bposición\b", r"\baseps"],
    "steps": [r"\*\*Técnica:", r"\*\*Flujo:", r"\*\*Paso", r"\bTécnica\b"],
    "confirmation": [r"\*\*Confirmación", r"\bconfirm"],
    "stop_points": [r"\*\*STOP", r"\bSTOP\b"],
    "complications": [r"\*\*Complicaciones?", r"\bcomplic"],
    "rescue": [r"\brescate\b", r"\bsi falla\b", r"\bplan [ABCD]\b"],
    "aftercare": [r"\*\*Después", r"\bcuidados posteriores\b", r"\breevalu"],
    "documentation": [r"\*\*Documentación", r"\bdocument"],
    "sources": [r"\*\*Fuentes?", r"\bBTF\b", r"\bERC\b", r"\bAHA\b", r"\bBTS\b", r"\bCDC\b", r"\bACOG\b", r"\bRCOG\b", r"\bDAS\b", r"\bACEP\b"],
}

REQUIRED_FOR_MIGRATION = tuple(FIELD_PATTERNS)

def parse_cards():
    cards = []
    for path in sorted(PROC_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(HEADER.finditer(text))
        for i, match in enumerate(matches):
            level = match.group(3) or ""
            if "REFERENCIA" in level:
                continue
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            cards.append({
                "procedure_id": match.group(1),
                "title": match.group(2).strip(),
                "level": level or "UNSPECIFIED",
                "family_file": str(path.relative_to(ROOT)),
                "body": body,
            })
    dedup = {c["procedure_id"]: c for c in cards}
    return [dedup[k] for k in sorted(dedup)]

def field_present(body: str, patterns: list[str]) -> bool:
    return any(re.search(p, body, flags=re.I) for p in patterns)

def audit_card(card):
    present = {field: field_present(card["body"], patterns) for field, patterns in FIELD_PATTERNS.items()}
    missing = [field for field in REQUIRED_FOR_MIGRATION if not present[field]]
    return {
        "procedure_id": card["procedure_id"],
        "title": card["title"],
        "level": card["level"],
        "family_file": card["family_file"],
        "present_fields": [k for k, v in present.items() if v],
        "missing_fields": missing,
        "migration_ready": not missing,
        "status": "YELLOW",
        "human_review_required": True,
    }

def build_report():
    audited = [audit_card(c) for c in parse_cards()]
    counts = Counter()
    for item in audited:
        for field in item["missing_fields"]:
            counts[field] += 1
    ready = sum(1 for x in audited if x["migration_ready"])
    return {
        "schema_version": "1.0",
        "procedure_count": len(audited),
        "migration_ready_count": ready,
        "needs_structuring_count": len(audited) - ready,
        "field_gap_counts": dict(sorted(counts.items())),
        "policy": "Do not invent missing clinical content. A procedure migrates to canonical JSON only after every required field is explicit and sources are verified.",
        "procedures": audited,
    }

def main():
    report = build_report()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "procedure_count": report["procedure_count"],
        "migration_ready_count": report["migration_ready_count"],
        "needs_structuring_count": report["needs_structuring_count"],
    }, ensure_ascii=False))
    return 0 if report["procedure_count"] == 196 else 2

if __name__ == "__main__":
    raise SystemExit(main())
