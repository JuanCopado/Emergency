#!/usr/bin/env python3
import argparse
import re
from pediatric_numbers import positive, nonnegative, finite_number, finite_result


def cli_decimal(raw):
    """Keep the raw mantissa until nonzero-to-zero parse underflow is excluded."""
    text = raw.strip()
    if not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?', text):
        raise argparse.ArgumentTypeError('use a finite decimal with a point and no grouping')
    try:
        value = finite_number('argument', float(text))
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from None
    mantissa = text.lower().partition('e')[0]
    if value == 0 and any(digit in '123456789' for digit in mantissa):
        raise argparse.ArgumentTypeError('nonzero decimal must not underflow to zero')
    return value

@finite_result
def infusion_ml_h(drug_mg, volume_ml, dose_mcg_kg_min, weight_kg):
    drug_mg = positive('drug_mg', drug_mg)
    volume_ml = positive('volume_ml', volume_ml)
    dose_mcg_kg_min = nonnegative('dose_mcg_kg_min', dose_mcg_kg_min)
    weight_kg = positive('weight_kg', weight_kg)
    concentration_mcg_ml = positive('concentration_mcg_ml', drug_mg * 1000.0 / volume_ml)
    check_dose = positive if dose_mcg_kg_min > 0 else nonnegative
    required_mcg_min = check_dose('required_mcg_min', dose_mcg_kg_min * weight_kg)
    ml_min = check_dose('ml_min', required_mcg_min / concentration_mcg_ml)
    return {
        "concentration_mcg_ml": concentration_mcg_ml,
        "required_mcg_min": required_mcg_min,
        "ml_min": ml_min,
        "ml_h": ml_min * 60.0,
    }


@finite_result
def fixed_dose_ml_h(dose_per_hour, concentration_per_ml):
    """Pump rate for non-weight-based doses (units/h, mg/h, micrograms/h).

    Dose and concentration must use the same amount unit (e.g. units/h with
    units/mL). Convert per-minute doses to per-hour before calling.
    """
    dose_per_hour = nonnegative('dose_per_hour', dose_per_hour)
    concentration_per_ml = positive('concentration_per_ml', concentration_per_ml)
    result = dose_per_hour / concentration_per_ml
    return positive('ml_h', result) if dose_per_hour > 0 else result


@finite_result
def weight_per_hour_ml_h(dose_per_kg_per_hour, weight_kg, concentration_per_ml):
    """Pump rate for weight-based per-hour doses (e.g. micrograms/kg/h, mg/kg/h)."""
    dose_per_kg_per_hour = nonnegative('dose_per_kg_per_hour', dose_per_kg_per_hour)
    weight_kg = positive('weight_kg', weight_kg)
    amount = dose_per_kg_per_hour * weight_kg
    if dose_per_kg_per_hour > 0:
        amount = positive('dose_per_hour', amount)
    return fixed_dose_ml_h(amount, concentration_per_ml)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--drug-mg", type=cli_decimal, required=True)
    p.add_argument("--volume-ml", type=cli_decimal, required=True)
    p.add_argument("--dose-mcg-kg-min", type=cli_decimal, required=True)
    p.add_argument("--weight-kg", type=cli_decimal, required=True)
    a = p.parse_args()
    print(infusion_ml_h(a.drug_mg, a.volume_ml, a.dose_mcg_kg_min, a.weight_kg))
