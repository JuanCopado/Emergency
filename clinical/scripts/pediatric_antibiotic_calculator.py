#!/usr/bin/env python3
"""Syndrome-specific pediatric antibiotic dose calculator.

Selection must occur upstream from the relevant syndrome/guideline.
This tool performs arithmetic only and never substitutes a dose from another syndrome.
"""

import json
from pathlib import Path
from pediatric_numbers import positive, finite_result
from ceftriaxone_sepsis_safety import TARGET_ENTRY_ID, CeftriaxoneSafetyError, validate_context

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-antibiotics.json"

from cli_paths import input_file

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {x["id"]: x for x in data["entries"]}

@finite_result
def calculate(entry_id, weight_kg, path=DEFAULT_REGISTRY, *, context=None):
    try:
        weight = positive("weight_kg", weight_kg)
    except ValueError:
        if entry_id == TARGET_ENTRY_ID:
            raise CeftriaxoneSafetyError("INVALID_WEIGHT", "weight_kg must be a positive finite number.") from None
        raise
    item = load_registry(path).get(entry_id)
    if not item:
        raise ValueError(f"unknown antibiotic entry: {entry_id}")
    if item.get("dose_automation") is False or item.get("status") in {"agent_verified_dose_external", "source_verified_selection_dose_external"}:
        raise ValueError(f"{entry_id}: agent is verified but pediatric dose remains delegated to an external dose source")
    guarded_context = validate_context(item, weight, context) if entry_id == TARGET_ENTRY_ID else None
    result = {
        "id": entry_id,
        "syndrome": item.get("syndrome"),
        "drug": item.get("drug"),
        "weight_kg": weight,
        "route": item.get("route"),
        "frequency": item.get("frequency"),
    }
    if guarded_context is not None:
        result.update(guarded_context)
        result["dose_per_kg"] = item["dose_per_kg"]
        result["dose_per_kg_unit"] = item["dose_unit"]
    if item.get("dose_per_kg") is not None:
        dose = positive("calculated dose", positive("dose_per_kg", item["dose_per_kg"]) * weight)
        if item.get("max_dose") is not None:
            dose = min(dose, positive("max_dose", item["max_dose"]))
        result["dose"] = dose
        result["dose_unit"] = "mg" if guarded_context is not None else item.get("dose_unit")
        conc = item.get("source_concentration_per_ml")
        if conc is not None:
            result["volume_ml"] = dose / positive("source_concentration_per_ml", conc)
        return result
    if item.get("dose_per_kg_min") is not None and item.get("dose_per_kg_max") is not None:
        low = positive("calculated dose", positive("dose_per_kg_min", item["dose_per_kg_min"]) * weight)
        high = positive("calculated dose", positive("dose_per_kg_max", item["dose_per_kg_max"]) * weight)
        if item.get("max_dose") is not None:
            cap = positive("max_dose", item["max_dose"])
            low = min(low, cap)
            high = min(high, cap)
        result["dose_range"] = [low, high]
        result["dose_unit"] = item.get("dose_unit")
        return result
    raise ValueError(f"{entry_id}: no arithmetic dose stored")

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("entry_id")
    p.add_argument("weight_kg", type=float)
    p.add_argument("--registry", type=input_file, default=DEFAULT_REGISTRY)
    p.add_argument("--context-json", type=input_file, help="Path to an explicit clinical-context JSON object; no environment fallback")
    args=p.parse_args()
    context = None
    if args.context_json is not None:
        context = json.loads(args.context_json.read_text(encoding="utf-8"))
        if not isinstance(context, dict):
            raise ValueError("INVALID_CONTEXT: --context-json must contain a JSON object")
    print(json.dumps(calculate(args.entry_id,args.weight_kg,args.registry,context=context), indent=2))
