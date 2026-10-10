#!/usr/bin/env python3
"""Source-based pediatric bolus/non-infusion calculator.

It never selects the indication. It computes dose/volume only from a registry entry.
"""

import json
from pathlib import Path
from pediatric_numbers import positive, finite_result

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-bolus-medications.json"

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {x["id"]: x for x in data["entries"]}

@finite_result
def calculate(entry_id, weight_kg, path=DEFAULT_REGISTRY):
    weight = positive("weight_kg", weight_kg)
    item = load_registry(path).get(entry_id)
    if not item:
        raise ValueError(f"unknown entry: {entry_id}")

    result = {"id": entry_id, "drug": item["drug"], "weight_kg": weight, "route": item.get("route")}

    if "fixed_dose" in item:
        result["dose"] = positive("fixed_dose", item["fixed_dose"])
        result["dose_unit"] = item["fixed_dose_unit"]
        return result

    if "dose_per_kg" in item:
        dose = positive("calculated dose", positive("dose_per_kg", item["dose_per_kg"]) * weight)
        max_dose = item.get("max_dose")
        if max_dose is not None:
            dose = min(dose, positive("max_dose", max_dose))
        result["dose"] = dose
        result["dose_unit"] = item["dose_unit"]

        if item["dose_unit"] == "mL/kg":
            result["volume_ml"] = dose
            return result

        concentration = item.get("source_concentration_per_ml")
        if concentration is not None:
            result["volume_ml"] = dose / positive("source_concentration_per_ml", concentration)
            result["concentration_per_ml"] = positive("source_concentration_per_ml", concentration)
            result["concentration_unit"] = item.get("concentration_unit")
        return result

    if "dose_per_kg_min" in item and "dose_per_kg_max" in item:
        low = positive("calculated dose", positive("dose_per_kg_min", item["dose_per_kg_min"]) * weight)
        high = positive("calculated dose", positive("dose_per_kg_max", item["dose_per_kg_max"]) * weight)
        max_dose = item.get("max_dose")
        if max_dose is not None:
            low = min(low, positive("max_dose", max_dose))
            high = min(high, positive("max_dose", max_dose))
        result["dose_range"] = [low, high]
        result["dose_unit"] = item["dose_unit"]
        concentration = item.get("source_concentration_per_ml")
        if concentration is not None:
            result["volume_range_ml"] = [low / positive("source_concentration_per_ml", concentration), high / positive("source_concentration_per_ml", concentration)]
        return result

    raise ValueError(f"{entry_id}: unsupported registry shape")

@finite_result
def calculate_with_selected_concentration(entry_id, weight_kg, concentration_per_ml, path=DEFAULT_REGISTRY):
    """Convert a source-verified dose to mL using the actual selected product concentration.

    The concentration is supplied at the point of use; this function never assumes
    a commercial liquid strength.
    """
    concentration = positive("concentration_per_ml", concentration_per_ml)
    if concentration <= 0:
        raise ValueError("concentration_per_ml must be > 0")
    result = calculate(entry_id, weight_kg, path)
    if "dose" not in result:
        raise ValueError(f"{entry_id}: a single numeric dose is required for mL conversion")
    result = dict(result)
    result["selected_concentration_per_ml"] = concentration
    result["volume_ml"] = float(result["dose"]) / concentration
    return result

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("entry_id")
    p.add_argument("weight_kg", type=float)
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args = p.parse_args()
    print(json.dumps(calculate(args.entry_id, args.weight_kg, args.registry), indent=2))
