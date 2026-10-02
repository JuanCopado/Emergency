#!/usr/bin/env python3
"""Deterministic pediatric DKA arithmetic; does not select treatment."""

def _positive(name, value):
    value=float(value)
    if value <= 0: raise ValueError(f'{name} must be > 0')
    return value

def corrected_sodium(measured_na, glucose_mmol_l):
    return float(measured_na) + 0.4*(float(glucose_mmol_l)-5.5)

def insulin_ml_h(weight_kg, units_per_kg_h, concentration_units_ml):
    w=_positive('weight_kg',weight_kg); d=_positive('units_per_kg_h',units_per_kg_h); c=_positive('concentration_units_ml',concentration_units_ml)
    return w*d/c

def cerebral_injury_rescue(weight_kg):
    w=_positive('weight_kg',weight_kg)
    # mannitol 20% = 0.2 g/mL; dose 0.5 g/kg
    return {'mannitol_20_percent_ml':(0.5*w)/0.2,'hypertonic_3_percent_ml':3.0*w}
