#!/usr/bin/env python3
"""Pediatric acute respiratory-support arithmetic."""

from pediatric_numbers import positive as _positive, nonnegative, finite_result

@finite_result
def hfno_flow_l_min(weight_kg):
    """RCH HFNP formula: <=12 kg 2 L/kg/min; >12 add 0.5 L/kg/min above 12; max 50."""
    w=_positive("weight_kg", weight_kg)
    if w <= 12:
        return 2.0*w
    return min(24.0 + 0.5*(w-12.0), 50.0)

@finite_result
def ventilation_rate_reference(age_years):
    """ERC/RCUK 2025 pragmatic supported-ventilation rate reference."""
    age=nonnegative("age_years", age_years)
    if age < 0:
        raise ValueError("age_years must be >= 0")
    if age < 1:
        return 25
    if age <= 8:
        return 20
    if age <= 12:
        return 15
    return 10
