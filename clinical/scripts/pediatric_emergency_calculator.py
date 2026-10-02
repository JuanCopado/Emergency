#!/usr/bin/env python3
"""Deterministic pediatric dose/fluid arithmetic.

This module performs arithmetic only. It does not select a drug, dose, concentration,
route or indication. Those inputs must come from a verified clinical/local source.
"""

def _positive(name, value):
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value

def weight_based_total(dose_per_kg, weight_kg, max_dose=None):
    dose = _positive("dose_per_kg", dose_per_kg)
    weight = _positive("weight_kg", weight_kg)
    total = dose * weight
    capped = False
    if max_dose is not None:
        maximum = _positive("max_dose", max_dose)
        if total > maximum:
            total = maximum
            capped = True
    return {"total_dose": total, "capped": capped}

def volume_for_dose(total_dose, concentration_per_ml):
    total = _positive("total_dose", total_dose)
    concentration = _positive("concentration_per_ml", concentration_per_ml)
    return total / concentration

def infusion_per_kg_min_ml_h(dose_per_kg_min, weight_kg, concentration_per_ml):
    dose = _positive("dose_per_kg_min", dose_per_kg_min)
    weight = _positive("weight_kg", weight_kg)
    concentration = _positive("concentration_per_ml", concentration_per_ml)
    return dose * weight * 60.0 / concentration

def infusion_per_kg_hour_ml_h(dose_per_kg_hour, weight_kg, concentration_per_ml):
    dose = _positive("dose_per_kg_hour", dose_per_kg_hour)
    weight = _positive("weight_kg", weight_kg)
    concentration = _positive("concentration_per_ml", concentration_per_ml)
    return dose * weight / concentration

def fluid_bolus_ml(weight_kg, ml_per_kg=10):
    weight = _positive("weight_kg", weight_kg)
    factor = _positive("ml_per_kg", ml_per_kg)
    return weight * factor

def maintenance_ml_day(weight_kg):
    """Holliday-Segar daily maintenance for children/young people."""
    weight = _positive("weight_kg", weight_kg)
    if weight <= 10:
        return 100.0 * weight
    if weight <= 20:
        return 1000.0 + 50.0 * (weight - 10.0)
    return 1500.0 + 20.0 * (weight - 20.0)

def maintenance_ml_h(weight_kg):
    return maintenance_ml_day(weight_kg) / 24.0

def gastroenteritis_deficit_ml(weight_kg, had_shock):
    """NICE CG84 IV deficit reference: 100 mL/kg after shock, 50 mL/kg otherwise."""
    return fluid_bolus_ml(weight_kg, 100 if had_shock else 50)
