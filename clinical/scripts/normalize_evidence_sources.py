#!/usr/bin/env python3
"""Normalize legacy module-level evidence metadata into a source catalog.

This script is deliberately conservative: it never splits a compound legacy
citation unless the repository contains independently verified source identities.
Unknown metadata remains null rather than being inferred.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
CLINICAL_ROOT = HERE.parents[1]
REGISTRY_PATH = CLINICAL_ROOT / "references" / "evidence-registry.json"
OUTPUT_PATH = CLINICAL_ROOT / "references" / "evidence-sources.json"\nOVERRIDES_PATH = CLINICAL_ROOT / "references" / "evidence-source-overrides.json"

ORG_PATTERNS = [
    (re.compile(r"AHA/ASA|American Heart Association", re.I), "AHA/ASA"),
    (re.compile(r"\bESC\b|European Society of Cardiology", re.I), "ESC"),
    (re.compile(r"\bERC\b|European Resuscitation Council", re.I), "ERC"),
    (re.compile(r"Resuscitation Council UK|\bRCUK\b", re.I), "Resuscitation Council UK"),
    (re.compile(r"\bNICE\b", re.I), "NICE"),
    (re.compile(r"\bACOG\b", re.I), "ACOG"),
    (re.compile(r"\bSCCM\b", re.I), "SCCM"),
    (re.compile(r"Surviving Sepsis Campaign", re.I), "Surviving Sepsis Campaign"),
    (re.compile(r"\bAASLD\b", re.I), "AASLD"),
    (re.compile(r"\bIDSA\b", re.I), "IDSA"),
    (re.compile(r"\bEAU\b", re.I), "EAU"),
    (re.compile(r"\bKDIGO\b", re.I), "KDIGO"),
    (re.compile(r"\bABA\b|American Burn Association", re.I), "American Burn Association"),
    (re.compile(r"\bACEP\b", re.I), "ACEP"),
    (re.compile(r"\bACG\b|American College of Gastroenterology", re.I), "ACG"),
    (re.compile(r"\bESGE\b", re.I), "ESGE"),
    (re.compile(r"\bESVS\b", re.I), "ESVS"),
    (re.compile(r"\bWSES\b", re.I), "WSES"),
    (re.compile(r"\bERS\b", re.I), "ERS"),
    (re.compile(r"\bATS\b", re.I), "ATS"),
    (re.compile(r"\bBTS\b", re.I), "BTS"),
    (re.compile(r"\bCPS\b|Canadian Paediatric Society", re.I), "Canadian Paediatric Society"),
    (re.compile(r"\bHSE\b", re.I), "HSE"),
    (re.compile(r"\bCDC\b", re.I), "CDC"),
    (re.compile(r"\bEMA\b", re.I), "EMA"),
    (re.compile(r"Society for Endocrinology", re.I), "Society for Endocrinology"),
]


def fnv1a_utf16(text: str) -> str:
    """Match JavaScript FNV-1a over UTF-16 code units for stable IDs."""
    value = 0x811C9DC5
    raw = text.encode("utf-16le")
    for idx in range(0, len(raw), 2):
        code_unit = raw[idx] | (raw[idx + 1] << 8)
        value ^= code_unit
        value = (value * 0x01000193) & 0xFFFFFFFF
    return f"{value:08x}"


def classify(title: str) -> str:
    lowered = title.lower()
    if re.search(r"product|label|smpc|rcm|dailymed", lowered):
        return "regulatory_product_info"
    if "consensus" in lowered:
        return "consensus"
    if re.search(r"guideline|guidance|cpg|practice bulletin|criteria|pathway", lowered):
        return "guideline"
    if re.search(r"review|position paper|study|trial", lowered):
        return "literature"
    if "workflow" in lowered:
        return "internal_workflow"
    return "other"


def organization(title: str) -> str | None:
    for pattern, name in ORG_PATTERNS:
        if pattern.search(title):
            return name
    return None


def persistent_id(url: str | None) -> str | None:
    if not url:
        return None
    match = re.search(r"doi\.org/(.+)$", url, flags=re.I)
    return f"doi:{match.group(1)}" if match else None


def normalize(registry_doc: dict, overrides_doc: dict | None = None) -> dict:
    by_id: dict[str, dict] = {}
    keys: dict[str, str] = {}
    module_sources: dict[str, list[dict]] = {}

    for module_id, record in registry_doc.get("modules", {}).items():
        title = (record.get("primary_source") or "").strip()
        url = record.get("primary_source_url") or None
        key = (url or title).strip()
        source_id = f"src-{fnv1a_utf16(key)}"

        if source_id in keys and keys[source_id] != key:
            raise ValueError(f"source ID collision: {source_id}")
        keys[source_id] = key

        if source_id not in by_id:
            by_id[source_id] = {
                "source_id": source_id,
                "title": title,
                "organization": organization(title),
                "source_type": classify(title),
                "url": url,
                "persistent_id": persistent_id(url),
                "version": record.get("stored_version"),
                "publication_date": None,
                "last_verified": record.get("last_checked"),
                "language": None,
                "jurisdiction": None,
                "license_status": "unknown",
                "provenance": "legacy_evidence_registry",
                "compound_identity": bool(re.search(r";| plus ", title, flags=re.I)),
                "modules": [],
            }

        by_id[source_id]["modules"].append(module_id)
        module_sources[module_id] = [{
            "source_id": source_id,
            "role": "primary_or_compound",
            "claim_scope": "module-level",
        }]

    overrides_doc = overrides_doc or {}
    override_modules = overrides_doc.get("module_sources", {})
    override_sources = overrides_doc.get("sources", [])

    # Replace legacy module mappings only for explicitly verified override modules.
    for module_id, refs in override_modules.items():
        if module_id not in module_sources:
            raise ValueError(f"override references unknown module: {module_id}")
        module_sources[module_id] = refs

    # Remove legacy generated sources that are no longer referenced after overrides.
    referenced_ids = {
        ref["source_id"]
        for refs in module_sources.values()
        for ref in refs
    }
    by_id = {
        source_id: source
        for source_id, source in by_id.items()
        if source_id in referenced_ids
    }

    for source in override_sources:
        source_id = source.get("source_id")
        if not source_id:
            raise ValueError("override source without source_id")
        if source_id in by_id:
            raise ValueError(f"override source_id collides with generated source: {source_id}")
        by_id[source_id] = dict(source)

    # Ensure every relationship resolves after overrides.
    known_ids = set(by_id)
    unresolved = sorted(
        {
            ref["source_id"]
            for refs in module_sources.values()
            for ref in refs
            if ref.get("source_id") not in known_ids
        }
    )
    if unresolved:
        raise ValueError(f"unresolved source IDs after overrides: {unresolved}")

    # Recompute reverse module lists from authoritative relationships.
    reverse = {source_id: [] for source_id in by_id}
    for module_id, refs in module_sources.items():
        for ref in refs:
            reverse[ref["source_id"]].append(module_id)
    for source_id, source in by_id.items():
        source["modules"] = sorted(set(reverse[source_id]))

    sources = sorted(by_id.values(), key=lambda item: item["source_id"])

    return {
        "schema_version": "1.0",
        "generated_from": "clinical/references/evidence-registry.json",
        "generated_by": "clinical/scripts/normalize_evidence_sources.py",
        "normalization_policy": {
            "no_source_splitting_without_verified_identity": True,
            "compound_legacy_sources_flagged": True,
            "unknown_metadata_is_null": True,
            "clinical_recommendations_modified": False,
        },
        "sources": sources,
        "module_sources": module_sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", default=str(OUTPUT_PATH))
    args = parser.parse_args()

    registry_doc = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))\n    overrides_doc = (\n        json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))\n        if OVERRIDES_PATH.is_file() else {}\n    )\n    normalized = normalize(registry_doc, overrides_doc)
    output_path = Path(args.output)

    if args.check:
        if not output_path.is_file():
            print(f"missing normalized source catalog: {output_path}")
            return 1
        current = json.loads(output_path.read_text(encoding="utf-8"))
        if current != normalized:
            print("normalized source catalog is stale; regenerate it")
            return 1
        print(
            f"EVIDENCE SOURCE CATALOG OK: "
            f"{len(normalized['sources'])} sources / "
            f"{len(normalized['module_sources'])} modules"
        )
        return 0

    output_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"WROTE {len(normalized['sources'])} sources for "
        f"{len(normalized['module_sources'])} modules"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
