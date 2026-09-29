#!/usr/bin/env python3
"""Calculate serum osmolar indices and electrolyte-free water clearance."""

import argparse
import json
import math


def _number(name, value, required=False):
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return value


def calculate(data):
    sodium = _number("serum_na_mmol_l", data.get("serum_na_mmol_l"), True)
    glucose = _number("glucose_mmol_l", data.get("glucose_mmol_l"))
    if glucose is None and data.get("glucose_mg_dl") is not None:
        glucose = _number("glucose_mg_dl", data.get("glucose_mg_dl")) / 18.0
    urea = _number("urea_mmol_l", data.get("urea_mmol_l"))
    if urea is None and data.get("bun_mg_dl") is not None:
        urea = _number("bun_mg_dl", data.get("bun_mg_dl")) / 2.8

    result = {"serum_na_mmol_l": sodium}
    if glucose is not None:
        result["effective_tonicity_mosm_kg"] = 2 * sodium + glucose
    if glucose is not None and urea is not None:
        calculated = 2 * sodium + glucose + urea
        result["calculated_serum_osmolality_mosm_kg"] = calculated
        measured = _number("measured_serum_osmolality_mosm_kg",
                           data.get("measured_serum_osmolality_mosm_kg"))
        if measured is not None:
            result["osmolal_gap_mosm_kg"] = measured - calculated

    urine_osm = _number("urine_osmolality_mosm_kg",
                        data.get("urine_osmolality_mosm_kg"))
    if urine_osm is not None:
        result["urine_osmolality_mosm_kg"] = urine_osm
        result["urine_concentration_category"] = (
            "dilute_below_300" if urine_osm < 300 else
            "concentrated_above_800" if urine_osm > 800 else
            "intermediate_300_to_800")

    urine_na = _number("urine_na_mmol_l", data.get("urine_na_mmol_l"))
    urine_k = _number("urine_k_mmol_l", data.get("urine_k_mmol_l"))
    urine_volume = _number("urine_volume_ml_h", data.get("urine_volume_ml_h"))
    if urine_na is not None:
        result["urine_na_mmol_l"] = urine_na
        result["urine_sodium_category"] = (
            "renal_sodium_conservation_below_20" if urine_na < 20 else
            "not_low_interpret_with_diuretics_and_renal_context")
    if urine_na is not None and urine_k is not None and urine_volume is not None:
        clearance = urine_volume * (1 - (urine_na + urine_k) / sodium)
        result["electrolyte_free_water_clearance_ml_h"] = clearance
        result["renal_water_balance_interpretation"] = (
            "ongoing_renal_electrolyte_free_water_loss" if clearance > 0 else
            "renal_electrolyte_free_water_retention" if clearance < 0 else
            "neutral")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_input", nargs="?", help="JSON object; defaults to stdin")
    args = parser.parse_args()
    payload = json.loads(args.json_input) if args.json_input else json.load(__import__("sys").stdin)
    print(json.dumps(calculate(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
