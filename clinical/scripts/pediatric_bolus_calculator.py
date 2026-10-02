#!/usr/bin/env python3
"""Source-based pediatric bolus/non-infusion calculator.

It never selects the indication. It computes dose/volume only from a registry entry.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-bolus-medications.json"

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {x["id"]: x for x in data["entries"]}

def calculate(entry_id, weight_kg, path=DEFAULT_REGISTRY):
    weight = float(weight_kg)
    if weight <= 0:
        raise ValueError("weight_kg must be > 0")
    item = load_registry(path).get(entry_id)
    if not item:
        raise ValueError(f"unknown entry: {entry_id}")

    result = {"id": entry_id, "drug": item["drug"], "weight_kg": weight, "route": item.get("route")}

    if "fixed_dose" in item:
        result["dose"] = float(item["fixed_dose"])
        result["dose_unit"] = item["fixed_dose_unit"]
        return result

    if "dose_per_kg" in item:
        dose = float(item["dose_per_kg"]) * weight
        max_dose = item.get("max_dose")
        if max_dose is not None:
            dose = min(dose, float(max_dose))
        result["dose"] = dose
        result["dose_unit"] = item["dose_unit"]

        if item["dose_unit"] == "mL/kg":
            result["volume_ml"] = dose
            return result

        concentration = item.get("source_concentration_per_ml")
        if concentration:
            result["volume_ml"] = dose / float(concentration)
            result["concentration_per_ml"] = float(concentration)
            result["concentration_unit"] = item.get("concentration_unit")
        return result

    if "dose_per_kg_min" in item and "dose_per_kg_max" in item:
        low = float(item["dose_per_kg_min"]) * weight
        high = float(item["dose_per_kg_max"]) * weight
        max_dose = item.get("max_dose")
        if max_dose is not None:
            low = min(low, float(max_dose))
            high = min(high, float(max_dose))
        result["dose_range"] = [low, high]
        result["dose_unit"] = item["dose_unit"]
        concentration = item.get("source_concentration_per_ml")
        if concentration:
            result["volume_range_ml"] = [low / float(concentration), high / float(concentration)]
        return result

    raise ValueError(f"{entry_id}: unsupported registry shape")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("entry_id")
    p.add_argument("weight_kg", type=float)
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args = p.parse_args()
    print(json.dumps(calculate(args.entry_id, args.weight_kg, args.registry), indent=2))
