#!/usr/bin/env python3
"""Deterministic pediatric blood-product arithmetic.

This script does not decide whether transfusion is indicated and does not define a
universal massive-transfusion pack. It calculates source-based component volumes.
"""

from pediatric_numbers import positive as _positive, finite_result

@finite_result
def trauma_rbc_ml(weight_kg, ml_per_kg=10):
    return _positive("weight_kg",weight_kg)*_positive("ml_per_kg",ml_per_kg)

@finite_result
def stable_rbc_ml(weight_kg, desired_hb_rise_g_l):
    w=_positive("weight_kg",weight_kg)
    rise=_positive("desired_hb_rise_g_l",desired_hb_rise_g_l)
    if w >= 20:
        raise ValueError("RCH mL formula is for children <20 kg; >20 kg use unit-based prescription and reassess")
    if rise > 20:
        raise ValueError("desired Hb rise exceeds the source usual 20 g/L increment")
    return w*0.5*rise

@finite_result
def stable_rbc_rate_ml_h(weight_kg, rate_ml_kg_h=5):
    return _positive("weight_kg",weight_kg)*_positive("rate_ml_kg_h",rate_ml_kg_h)

@finite_result
def platelets_ml(weight_kg):
    w=_positive("weight_kg",weight_kg)
    if w >= 15:
        raise ValueError("RCH weight-based platelet volume is for children <15 kg; >15 kg generally use one unit")
    return 10*w

@finite_result
def ffp_range_ml(weight_kg):
    w=_positive("weight_kg",weight_kg)
    return [10*w,20*w]

@finite_result
def cryoprecipitate_range_ml(weight_kg):
    w=_positive("weight_kg",weight_kg)
    return [5*w,10*w]

@finite_result
def noncritical_component_rate_range_ml_h(weight_kg):
    w=_positive("weight_kg",weight_kg)
    return [10*w,20*w]
