#!/usr/bin/env python3
"""Pediatric acute respiratory-support arithmetic."""

def _positive(name, value):
    value=float(value)
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value

def hfno_flow_l_min(weight_kg):
    """RCH HFNP formula: <=12 kg 2 L/kg/min; >12 add 0.5 L/kg/min above 12; max 50."""
    w=_positive("weight_kg", weight_kg)
    if w <= 12:
        return 2.0*w
    return min(24.0 + 0.5*(w-12.0), 50.0)

def ventilation_rate_reference(age_years):
    """ERC/RCUK 2025 pragmatic supported-ventilation rate reference."""
    age=float(age_years)
    if age < 0:
        raise ValueError("age_years must be >= 0")
    if age < 1:
        return 25
    if age <= 8:
        return 20
    if age <= 12:
        return 15
    return 10
