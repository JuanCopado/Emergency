#!/usr/bin/env python3
"""Deterministic pediatric DKA arithmetic; does not select treatment."""

from pediatric_numbers import positive as _positive, finite_result

@finite_result
def corrected_sodium(measured_na, glucose_mmol_l):
    return _positive("measured_na", measured_na) + 0.4*(_positive("glucose_mmol_l", glucose_mmol_l)-5.5)

@finite_result
def insulin_ml_h(weight_kg, units_per_kg_h, concentration_units_ml):
    w=_positive('weight_kg',weight_kg); d=_positive('units_per_kg_h',units_per_kg_h); c=_positive('concentration_units_ml',concentration_units_ml)
    return w*d/c

@finite_result
def cerebral_injury_rescue(weight_kg):
    w=_positive('weight_kg',weight_kg)
    # mannitol 20% = 0.2 g/mL; dose 0.5 g/kg
    return {'mannitol_20_percent_ml':(0.5*w)/0.2,'hypertonic_3_percent_ml':3.0*w}
