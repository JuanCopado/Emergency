#!/usr/bin/env python3
import argparse

def infusion_ml_h(drug_mg, volume_ml, dose_mcg_kg_min, weight_kg):
    concentration_mcg_ml = drug_mg * 1000.0 / volume_ml
    required_mcg_min = dose_mcg_kg_min * weight_kg
    ml_min = required_mcg_min / concentration_mcg_ml
    return {
        "concentration_mcg_ml": concentration_mcg_ml,
        "required_mcg_min": required_mcg_min,
        "ml_min": ml_min,
        "ml_h": ml_min * 60.0,
    }


def fixed_dose_ml_h(dose_per_hour, concentration_per_ml):
    """Pump rate for non-weight-based doses (units/h, mg/h, micrograms/h).

    Dose and concentration must use the same amount unit (e.g. units/h with
    units/mL). Convert per-minute doses to per-hour before calling.
    """
    if concentration_per_ml <= 0:
        raise ValueError("concentration must be positive")
    return dose_per_hour / concentration_per_ml


def weight_per_hour_ml_h(dose_per_kg_per_hour, weight_kg, concentration_per_ml):
    """Pump rate for weight-based per-hour doses (e.g. micrograms/kg/h, mg/kg/h)."""
    return fixed_dose_ml_h(dose_per_kg_per_hour * weight_kg, concentration_per_ml)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--drug-mg", type=float, required=True)
    p.add_argument("--volume-ml", type=float, required=True)
    p.add_argument("--dose-mcg-kg-min", type=float, required=True)
    p.add_argument("--weight-kg", type=float, required=True)
    a = p.parse_args()
    print(infusion_ml_h(a.drug_mg, a.volume_ml, a.dose_mcg_kg_min, a.weight_kg))
