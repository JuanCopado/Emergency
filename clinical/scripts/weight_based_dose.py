#!/usr/bin/env python3
import argparse

def weight_based_dose(weight_kg, dose_per_kg, max_dose=None):
    dose = weight_kg * dose_per_kg
    if max_dose is not None:
        dose = min(dose, max_dose)
    return dose

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--weight-kg", type=float, required=True)
    p.add_argument("--dose-per-kg", type=float, required=True)
    p.add_argument("--max-dose", type=float, default=None)
    a = p.parse_args()
    print(weight_based_dose(a.weight_kg, a.dose_per_kg, a.max_dose))
