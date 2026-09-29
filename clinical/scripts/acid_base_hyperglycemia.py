#!/usr/bin/env python3
"""Deterministic acid-base and hyperglycemic-crisis calculations.

Inputs are a JSON object. Values copied from an image must be visually verified
before use; this script does not perform OCR or establish a diagnosis by itself.
"""

import argparse
import json
import math
import sys


def _number(name, value, required=False):
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _glucose_mmol(data):
    value = _number("glucose_mmol_l", data.get("glucose_mmol_l"))
    if value is None and data.get("glucose_mg_dl") is not None:
        value = _number("glucose_mg_dl", data.get("glucose_mg_dl")) / 18.0
    return value


def _urea_mmol(data):
    value = _number("urea_mmol_l", data.get("urea_mmol_l"))
    if value is None and data.get("bun_mg_dl") is not None:
        value = _number("bun_mg_dl", data.get("bun_mg_dl")) / 2.8
    return value


def calculate(data):
    ph = _number("ph", data.get("ph"))
    pco2 = _number("pco2_mm_hg", data.get("pco2_mm_hg"))
    hco3 = _number("hco3_mmol_l", data.get("hco3_mmol_l"))
    sodium = _number("sodium_mmol_l", data.get("sodium_mmol_l"))
    chloride = _number("chloride_mmol_l", data.get("chloride_mmol_l"))
    albumin = _number("albumin_g_dl", data.get("albumin_g_dl"))
    glucose = _glucose_mmol(data)
    urea = _urea_mmol(data)
    pao2 = _number("pao2_mm_hg", data.get("pao2_mm_hg"))
    fio2 = _number("fio2_fraction", data.get("fio2_fraction"))
    atmospheric_pressure = _number(
        "atmospheric_pressure_mm_hg", data.get("atmospheric_pressure_mm_hg"))
    respiratory_quotient = _number(
        "respiratory_quotient", data.get("respiratory_quotient"))
    if respiratory_quotient is None:
        respiratory_quotient = 0.8
    if fio2 is not None and not 0 < fio2 <= 1:
        raise ValueError("fio2_fraction must be greater than 0 and at most 1")
    if pao2 is not None and pao2 < 0:
        raise ValueError("pao2_mm_hg must be non-negative")
    if atmospheric_pressure is not None and atmospheric_pressure <= 47:
        raise ValueError("atmospheric_pressure_mm_hg must be greater than 47")
    if respiratory_quotient <= 0:
        raise ValueError("respiratory_quotient must be positive")
    weight = _number("weight_kg", data.get("weight_kg"))
    insulin_concentration = _number(
        "insulin_concentration_units_ml",
        data.get("insulin_concentration_units_ml"))
    if insulin_concentration is None:
        insulin_concentration = 1.0
    if insulin_concentration <= 0:
        raise ValueError("insulin_concentration_units_ml must be positive")

    result = {}
    if ph is not None:
        result["ph_state"] = (
            "acidemia" if ph < 7.35 else
            "alkalemia" if ph > 7.45 else
            "reference_range_or_mixed_disorder")

    if ph is not None and pco2 is not None:
        result["calculated_hco3_from_henderson_hasselbalch_mmol_l"] = (
            0.03 * pco2 * (10 ** (ph - 6.1)))

    if pao2 is not None and fio2 is not None:
        result["pao2_fio2_ratio_mm_hg"] = pao2 / fio2
        result["oxygenation_safety"] = (
            "Quantifies oxygenation impairment only; do not diagnose ARDS from "
            "P/F ratio alone. Verify arterial sample, actual FiO2, respiratory "
            "support/PEEP, timing, imaging and edema origin.")
        if atmospheric_pressure is not None and pco2 is not None:
            alveolar_o2 = (fio2 * (atmospheric_pressure - 47.0)
                           - pco2 / respiratory_quotient)
            result["alveolar_o2_equation"] = {
                "assumed_respiratory_quotient": respiratory_quotient,
                "atmospheric_pressure_mm_hg": atmospheric_pressure,
                "calculated_alveolar_o2_mm_hg": alveolar_o2,
                "a_a_gradient_mm_hg": alveolar_o2 - pao2,
            }

    if all(value is not None for value in (sodium, chloride, hco3)):
        gap = sodium - chloride - hco3
        result["anion_gap_mmol_l"] = gap
        corrected_gap = gap
        if albumin is not None:
            corrected_gap = gap + 2.5 * (4.0 - albumin)
            result["albumin_corrected_anion_gap_mmol_l"] = corrected_gap
        if hco3 < 24 and corrected_gap > 12 and (24 - hco3) > 0:
            result["delta_ratio"] = (corrected_gap - 12) / (24 - hco3)

    if hco3 is not None and hco3 < 24:
        center = 1.5 * hco3 + 8
        result["winters_expected_pco2_mm_hg"] = {
            "center": center, "low": center - 2, "high": center + 2}
        if pco2 is not None:
            result["metabolic_acidosis_compensation"] = (
                "additional_respiratory_alkalosis" if pco2 < center - 2 else
                "additional_respiratory_acidosis" if pco2 > center + 2 else
                "appropriate_by_winters_formula")

    if hco3 is not None and hco3 > 24:
        center = 40 + 0.7 * (hco3 - 24)
        result["metabolic_alkalosis_expected_pco2_mm_hg"] = {
            "center": center, "low": center - 5, "high": center + 5}

    if pco2 is not None:
        delta = (pco2 - 40) / 10
        if pco2 > 40:
            result["respiratory_acidosis_expected_hco3_mmol_l"] = {
                "acute": 24 + delta,
                "chronic": 24 + 3.5 * delta}
        elif pco2 < 40:
            fall = (40 - pco2) / 10
            result["respiratory_alkalosis_expected_hco3_mmol_l"] = {
                "acute": 24 - 2 * fall,
                "chronic": 24 - 4 * fall}

    if sodium is not None and glucose is not None:
        result["effective_serum_osmolality_mosm_kg"] = 2 * sodium + glucose
        glucose_mg_dl = glucose * 18.0
        result["glucose_corrected_sodium_1_6_mmol_l"] = (
            sodium + 1.6 * max(glucose_mg_dl - 100, 0) / 100)
        if urea is not None:
            result["total_calculated_osmolality_mosm_kg"] = 2 * sodium + glucose + urea
            measured_osm = _number(
                "measured_serum_osmolality_mosm_kg",
                data.get("measured_serum_osmolality_mosm_kg"))
            if measured_osm is not None:
                result["osmolal_gap_mosm_kg"] = measured_osm - result[
                    "total_calculated_osmolality_mosm_kg"]

    beta = _number("beta_hydroxybutyrate_mmol_l",
                   data.get("beta_hydroxybutyrate_mmol_l"))
    urine_ketones = _number("urine_ketones_plus", data.get("urine_ketones_plus"))
    diabetes_history = data.get("history_of_diabetes") is True
    dka_d = diabetes_history or (glucose is not None and glucose >= 11.1)
    dka_k = ((beta is not None and beta >= 3.0) or
             (urine_ketones is not None and urine_ketones >= 2))
    dka_a = ((ph is not None and ph < 7.3) or
             (hco3 is not None and hco3 < 18))
    if any(value is not None for value in (glucose, beta, urine_ketones, ph, hco3)):
        result["dka_criteria"] = {
            "diabetes_or_hyperglycemia": dka_d,
            "ketosis": dka_k,
            "metabolic_acidosis": dka_a,
            "all_present": dka_d and dka_k and dka_a}

    effective_osm = result.get("effective_serum_osmolality_mosm_kg")
    total_osm = result.get("total_calculated_osmolality_mosm_kg")
    hhs = {
        "glucose_at_least_600_mg_dl": glucose is not None and glucose >= 33.3,
        "hyperosmolality": ((effective_osm is not None and effective_osm > 300) or
                            (total_osm is not None and total_osm > 320)),
        "no_significant_ketonemia": ((beta is not None and beta < 3.0) or
                                     (urine_ketones is not None and urine_ketones < 2)),
        "no_acidosis": (ph is not None and ph >= 7.3 and
                         hco3 is not None and hco3 >= 15)}
    if glucose is not None:
        hhs["all_present"] = all(hhs.values())
        result["hhs_criteria"] = hhs

    if weight is not None:
        dka_units_h = 0.1 * weight
        lower_units_h = 0.05 * weight
        result["insulin_infusion_reference"] = {
            "concentration_units_ml": insulin_concentration,
            "dka_or_mixed_initial_units_h": dka_units_h,
            "dka_or_mixed_initial_ml_h": dka_units_h / insulin_concentration,
            "dka_after_glucose_below_250_units_h": lower_units_h,
            "dka_after_glucose_below_250_ml_h": lower_units_h / insulin_concentration,
            "hhs_without_significant_ketosis_units_h": lower_units_h,
            "hhs_without_significant_ketosis_ml_h": lower_units_h / insulin_concentration,
            "safety": "Do not start insulin while potassium is below 3.5 mmol/L."}

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_input", nargs="?", help="JSON object; defaults to stdin")
    args = parser.parse_args()
    payload = json.loads(args.json_input) if args.json_input else json.load(sys.stdin)
    print(json.dumps(calculate(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
