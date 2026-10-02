#!/usr/bin/env python3
"""Pediatric burn resuscitation arithmetic using 3 mL/kg/%TBSA modified Parkland."""

def _positive(name, value):
    value=float(value)
    if value <= 0: raise ValueError(f'{name} must be > 0')
    return value

def maintenance_ml_day(weight_kg):
    w=_positive('weight_kg',weight_kg)
    if w <= 10: return 100*w
    if w <= 20: return 1000+50*(w-10)
    return 1500+20*(w-20)

def burn_plan(weight_kg, tbsa_percent, hours_since_burn=0):
    w=_positive('weight_kg',weight_kg); tbsa=_positive('tbsa_percent',tbsa_percent)
    if tbsa > 100: raise ValueError('tbsa_percent must be <=100')
    elapsed=float(hours_since_burn)
    if elapsed < 0: raise ValueError('hours_since_burn must be >=0')
    total=3.0*w*tbsa
    first=total/2.0; second=total/2.0
    remaining_first=max(0.0,8.0-elapsed)
    first_rate=(first/remaining_first) if remaining_first>0 else 0.0
    return {
      'resuscitation_24h_ml':total,
      'first_half_ml':first,
      'second_half_ml':second,
      'first_phase_hours_remaining':remaining_first,
      'first_phase_rate_ml_h':first_rate,
      'second_phase_rate_ml_h':second/16.0,
      'maintenance_ml_day':maintenance_ml_day(w),
      'maintenance_ml_h':maintenance_ml_day(w)/24.0,
      'urine_target_ml_h':w
    }
