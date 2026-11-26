#!/usr/bin/env python3
"""Project the versioned corticosteroid reference into the client; no clinical arithmetic."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "clinical/pharmacology/corticosteroids.json"
OUTPUT = ROOT / "app/src/corticosteroids/catalog.generated.json"


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def build_catalog(source_path=SOURCE):
    raw = source_path.read_bytes()
    data = json.loads(raw)
    if data["schema_version"] != "1.0" or data["module_id"] != "medication-selection-safety":
        raise ValueError("Unsupported corticosteroid reference contract")
    drugs = data["drugs"]
    ids = {drug["id"] for drug in drugs}
    if len(ids) != len(drugs) or not ids:
        raise ValueError("Duplicate or empty drug identifiers")
    sources = {source["id"] for source in data["sources"]}
    if len(sources) != len(data["sources"]):
        raise ValueError("Duplicate sources")
    if any(not source["url"].startswith("https://") or not source["locator"] or not source["version"] for source in data["sources"]):
        raise ValueError("Every source needs an HTTPS URL, version and locator")
    table_ids = set()
    for table in data["tables"]:
        if table["id"] in table_ids or table["source_id"] not in sources:
            raise ValueError("Duplicate table or missing source")
        table_ids.add(table["id"])
        rows = table["rows"]
        if len(rows) != len(ids) or {row["drug_id"] for row in rows} != ids:
            raise ValueError("Every table must describe each drug exactly once")
        for row in rows:
            duration = row["biological_half_life_hours"]
            if not positive(row["equivalent_mg"]) or len(duration) != 2 or not all(positive(v) for v in duration) or duration[0] > duration[1]:
                raise ValueError("Invalid equivalence or biological half-life")
    for drug in drugs:
        activity = drug["mineralocorticoid_relative_activity"]
        if type(activity) not in (int, float) or not math.isfinite(activity) or activity < 0 or drug["mineralocorticoid_source_id"] not in sources:
            raise ValueError("Invalid mineralocorticoid activity or source")
        if set(drug["name"]) != {"es", "pt", "en", "zh"}:
            raise ValueError("Missing drug-name locale")
    if data["scope"]["supported_routes"] != ["oral", "iv"] or data["scope"]["unit"] != "mg":
        raise ValueError("The comparator is limited to systemic oral/IV mg")
    for regimen in data["hydrocortisone"].values():
        if any(source not in sources for source in regimen["source_ids"]):
            raise ValueError("Unknown regimen source")
    for row in data["hydrocortisone"]["pediatric_adrenal_crisis"]["rows"]:
        doses = row["maintenance_mg"]
        if not positive(row["initial_mg"]) or len(doses) != 2 or not all(positive(v) for v in doses) or doses[0] > doses[1]:
            raise ValueError("Invalid pediatric reference range")
    short = data["short_courses"]
    bell = short["bell_palsy"]
    regimen = bell["reference_regimen"]
    if bell["module_id"] != "ent-emergencies" or bell["section_id"] != "bell-palsy" or bell["adult_draft_min_age_years"] != 18:
        raise ValueError("Bell reference must reuse ENT and keep the adult draft boundary")
    if regimen["drug_id"] not in ids or regimen["route"] != "oral" or regimen["source_id"] not in sources:
        raise ValueError("Invalid Bell source regimen")
    if not all(positive(regimen[key]) for key in ("dose_mg", "interval_hours", "duration_days", "total_mg_per_day")):
        raise ValueError("Invalid Bell regimen quantity")
    for reference in (bell, short["duration_withdrawal"]):
        if not reference["source_ids"] or any(source not in sources for source in reference["source_ids"]):
            raise ValueError("Unknown short-course source")
    related = {module["id"] for module in data["related_modules"]}
    if not short["existing_module_ids"] or any(module not in related for module in short["existing_module_ids"]):
        raise ValueError("Short-course links must reuse existing references")
    return {"source_path": "clinical/pharmacology/corticosteroids.json",
            "source_sha256": hashlib.sha256(raw).hexdigest(), **data}


def rendered_catalog(source_path=SOURCE):
    return json.dumps(build_catalog(source_path), ensure_ascii=False, indent=2) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    expected = rendered_catalog()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("Corticosteroid projection is stale; run clinical/scripts/build_corticosteroid_catalog.py")
            return 1
        print("Corticosteroid projection matches its canonical source.")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print("Generated corticosteroid reference: 2 attributed tables; adult and pediatric scopes separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
