#!/usr/bin/env python3
"""Deterministic pediatric IV-fluid arithmetic.

This calculator does not diagnose shock/dehydration and does not choose a syndrome.
It only calculates volumes/rates for a plan already selected from a verified pathway.
"""

def _positive(name, value):
    value=float(value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value

def maintenance_ml_day(weight_kg):
    w=_positive("weight_kg", weight_kg)
    if w <= 10:
        return 100*w
    if w <= 20:
        return 1000 + 50*(w-10)
    return 1500 + 20*(w-20)

def maintenance_ml_h(weight_kg, fraction=1.0):
    f=_positive("fraction", fraction)
    return maintenance_ml_day(weight_kg)*f/24.0

def shock_bolus(weight_kg, ml_per_kg=10, minutes=10):
    w=_positive("weight_kg", weight_kg)
    vpk=_positive("ml_per_kg", ml_per_kg)
    mins=_positive("minutes", minutes)
    volume=w*vpk
    return {"volume_ml": volume, "minutes": mins, "equivalent_ml_h": volume*60/mins}

def ors_rehydration(weight_kg, ml_per_kg=50, hours=4):
    w=_positive("weight_kg", weight_kg)
    vpk=_positive("ml_per_kg", ml_per_kg)
    h=_positive("hours", hours)
    volume=w*vpk
    return {"volume_ml": volume, "hours": h, "average_ml_h": volume/h}

def dehydration_deficit_ml(weight_kg, percent_dehydration):
    w=_positive("weight_kg", weight_kg)
    pct=_positive("percent_dehydration", percent_dehydration)
    if pct > 20:
        raise ValueError("percent_dehydration implausibly high")
    return w*pct*10.0

def generic_deficit_48h_plan(weight_kg, percent_dehydration):
    """RCH-style generic >5% plan: first 5% in first 24h, remainder next 24h."""
    total=dehydration_deficit_ml(weight_kg, percent_dehydration)
    w=float(weight_kg)
    first=min(total, 50.0*w)
    second=max(0.0, total-first)
    return {
        "total_deficit_ml": total,
        "first_24h_deficit_ml": first,
        "first_24h_deficit_ml_h": first/24.0,
        "second_24h_deficit_ml": second,
        "second_24h_deficit_ml_h": second/24.0,
    }

def gastroenteritis_iv_deficit(weight_kg, shocked):
    w=_positive("weight_kg", weight_kg)
    return w*(100.0 if shocked else 50.0)

def hypernatremia_deficit_rate(weight_kg, percent_dehydration, hours=48):
    total=dehydration_deficit_ml(weight_kg, percent_dehydration)
    h=_positive("hours", hours)
    return {"deficit_ml": total, "hours": h, "deficit_ml_h": total/h}

def symptomatic_hyponatremia_bolus(weight_kg, ml_per_kg=2, max_ml=100, minutes=15):
    w=_positive("weight_kg", weight_kg)
    volume=min(w*_positive("ml_per_kg",ml_per_kg), _positive("max_ml",max_ml))
    mins=_positive("minutes",minutes)
    return {"volume_ml":volume,"minutes":mins,"equivalent_ml_h":volume*60/mins}
