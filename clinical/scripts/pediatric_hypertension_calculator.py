#!/usr/bin/env python3
"""Source-verified pediatric hypertensive-emergency pump arithmetic."""

def _positive(name, value):
    value=float(value)
    if value <= 0: raise ValueError(f'{name} must be > 0')
    return value

def labetalol_ml_h(weight_kg, dose_mg_kg_h, concentration_mg_ml):
    w=_positive('weight_kg',weight_kg); d=_positive('dose_mg_kg_h',dose_mg_kg_h); c=_positive('concentration_mg_ml',concentration_mg_ml)
    return w*d/c

def hydralazine_ml_h(weight_kg, dose_mcg_kg_min, concentration_mcg_ml=400):
    w=_positive('weight_kg',weight_kg); d=_positive('dose_mcg_kg_min',dose_mcg_kg_min); c=_positive('concentration_mcg_ml',concentration_mcg_ml)
    return w*d*60.0/c
