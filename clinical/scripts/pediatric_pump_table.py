#!/usr/bin/env python3
"""Generate pediatric pump tables only from source-verified doses and concentrations.

Fail-closed by design: unverified source data or missing concentration/dose ladders
raise ValueError rather than returning a pump rate.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-infusion-localization.json"

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {item["drug"]: item for item in data["drugs"]}

def pump_table(drug, weight_kg, path=DEFAULT_REGISTRY):
    weight = float(weight_kg)
    if weight <= 0:
        raise ValueError("weight_kg must be > 0")
    item = load_registry(path).get(drug)
    if not item:
        raise ValueError(f"unknown drug: {drug}")
    if item.get("status") != "source_verified":
        raise ValueError(f"{drug}: dose/concentration source is not verified")
    concentration = item.get("final_concentration_per_ml")
    doses = item.get("dose_ladder") or []
    if not concentration or float(concentration) <= 0:
        raise ValueError(f"{drug}: final concentration missing")
    if not doses:
        raise ValueError(f"{drug}: dose ladder missing")
    concentration = float(concentration)
    unit = item.get("dose_unit")
    rows = []
    for raw in doses:
        dose = float(raw)
        if dose <= 0:
            raise ValueError(f"{drug}: invalid dose ladder")
        if unit == "micrograms/kg/min":
            ml_h = dose * weight * 60.0 / concentration
        elif unit in {"micrograms/kg/hour", "milligrams/kg/hour"}:
            ml_h = dose * weight / concentration
        else:
            raise ValueError(f"{drug}: unsupported dose unit {unit}")
        rows.append({"dose": dose, "dose_unit": unit, "ml_h": ml_h})
    return {
        "drug": drug,
        "weight_kg": weight,
        "concentration_per_ml": concentration,
        "concentration_unit": item.get("concentration_unit"),
        "rows": rows,
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("drug")
    parser.add_argument("weight_kg", type=float)
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    args = parser.parse_args()
    print(json.dumps(pump_table(args.drug, args.weight_kg, args.registry), indent=2))
