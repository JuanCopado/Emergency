#!/usr/bin/env python3
"""Generate pediatric pump tables from source-verified dose/concentration data.

Fail-closed by design:
- unverified or product-restricted/off-label entries are rejected;
- missing concentrations/dose ladders are rejected;
- structured source restrictions (for example max_weight_kg) are enforced.
"""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DEFAULT_REGISTRY = ROOT / "qa" / "pediatric-infusion-localization.json"

ALLOWED_STATUSES = {"source_verified", "source_verified_with_restriction"}

def load_registry(path=DEFAULT_REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {item["drug"]: item for item in data["drugs"]}

def _resolved_concentration(item, weight):
    mode = item.get("preparation_mode")
    if mode == "fixed_concentration":
        value = item.get("final_concentration_per_ml")
        if not value or float(value) <= 0:
            raise ValueError(f"{item['drug']}: final concentration missing")
        return float(value)
    if mode == "weight_normalized":
        amount_per_kg = item.get("drug_amount_per_kg")
        final_volume = item.get("final_volume_ml")
        unit = item.get("drug_amount_per_kg_unit")
        if not amount_per_kg or not final_volume:
            raise ValueError(f"{item['drug']}: weight-normalized preparation incomplete")
        if unit != "mg/kg" or item.get("concentration_unit") != "micrograms/mL":
            raise ValueError(f"{item['drug']}: unsupported weight-normalized units")
        total_micrograms = float(amount_per_kg) * 1000.0 * weight
        return total_micrograms / float(final_volume)
    raise ValueError(f"{item['drug']}: unsupported preparation mode {mode}")

def pump_table(drug, weight_kg, path=DEFAULT_REGISTRY):
    weight = float(weight_kg)
    if weight <= 0:
        raise ValueError("weight_kg must be > 0")
    item = load_registry(path).get(drug)
    if not item:
        raise ValueError(f"unknown drug: {drug}")
    if item.get("status") not in ALLOWED_STATUSES:
        raise ValueError(f"{drug}: source verification is insufficient for automatic pump-table generation")
    max_weight = item.get("max_weight_kg")
    if max_weight is not None and weight > float(max_weight):
        raise ValueError(f"{drug}: requested weight exceeds source-verified preparation range")
    doses = item.get("dose_ladder") or []
    if not doses:
        raise ValueError(f"{drug}: dose ladder missing")
    concentration = _resolved_concentration(item, weight)
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
        "preparation_mode": item.get("preparation_mode"),
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
