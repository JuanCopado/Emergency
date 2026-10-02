#!/usr/bin/env python3
"""Syndrome-specific pediatric antibiotic dose calculator.

Selection must occur upstream from the relevant syndrome/guideline.
This tool performs arithmetic only and never substitutes a dose from another syndrome.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-antibiotics.json"

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {x["id"]: x for x in data["entries"]}

def calculate(entry_id, weight_kg, path=DEFAULT_REGISTRY):
    weight = float(weight_kg)
    if weight <= 0:
        raise ValueError("weight_kg must be > 0")
    item = load_registry(path).get(entry_id)
    if not item:
        raise ValueError(f"unknown antibiotic entry: {entry_id}")
    if item.get("dose_automation") is False or item.get("status") in {"agent_verified_dose_external", "source_verified_selection_dose_external"}:
        raise ValueError(f"{entry_id}: agent is verified but pediatric dose remains delegated to an external dose source")
    result = {
        "id": entry_id,
        "syndrome": item.get("syndrome"),
        "drug": item.get("drug"),
        "weight_kg": weight,
        "route": item.get("route"),
        "frequency": item.get("frequency"),
    }
    if item.get("dose_per_kg") is not None:
        dose = float(item["dose_per_kg"]) * weight
        if item.get("max_dose") is not None:
            dose = min(dose, float(item["max_dose"]))
        result["dose"] = dose
        result["dose_unit"] = item.get("dose_unit")
        conc = item.get("source_concentration_per_ml")
        if conc:
            result["volume_ml"] = dose / float(conc)
        return result
    if item.get("dose_per_kg_min") is not None and item.get("dose_per_kg_max") is not None:
        low = float(item["dose_per_kg_min"]) * weight
        high = float(item["dose_per_kg_max"]) * weight
        if item.get("max_dose") is not None:
            cap = float(item["max_dose"])
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
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args=p.parse_args()
    print(json.dumps(calculate(args.entry_id,args.weight_kg,args.registry), indent=2))
