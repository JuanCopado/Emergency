#!/usr/bin/env python3
"""Deterministic serial ROX calculations for adult HFNO review.

This calculator does not decide whether to intubate. Published cutoffs were
validated in adults with pneumonia and must be integrated with bedside status.
"""

import argparse
import json
import math
import sys


FAILURE_CUTOFFS = {2.0: 2.85, 6.0: 3.47, 12.0: 3.85}
LOWER_RISK_CUTOFF = 4.88


def _number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _classify(hours, rox):
    failure = FAILURE_CUTOFFS.get(hours)
    if failure is None:
        return "no_validated_time_specific_zone"
    if rox < failure:
        return "higher_failure_risk_signal_in_original_pneumonia_cohort"
    if rox >= LOWER_RISK_CUTOFF:
        return "lower_intubation_risk_signal_in_original_pneumonia_cohort"
    return "indeterminate_zone_requires_close_reassessment"


def calculate(data):
    observations = data.get("observations")
    if not isinstance(observations, list) or not observations:
        raise ValueError("observations must be a non-empty list")

    results = []
    for index, item in enumerate(observations):
        if not isinstance(item, dict):
            raise ValueError(f"observations[{index}] must be an object")
        hours = _number(f"observations[{index}].hours", item.get("hours"))
        spo2 = _number(f"observations[{index}].spo2_percent",
                       item.get("spo2_percent"))
        fio2 = _number(f"observations[{index}].fio2_fraction",
                       item.get("fio2_fraction"))
        rate = _number(f"observations[{index}].respiratory_rate_min",
                       item.get("respiratory_rate_min"))
        if hours < 0:
            raise ValueError("hours must be non-negative")
        if not 0 < spo2 <= 100:
            raise ValueError("spo2_percent must be greater than 0 and at most 100")
        if not 0.21 <= fio2 <= 1:
            raise ValueError("fio2_fraction must be between 0.21 and 1")
        if rate <= 0:
            raise ValueError("respiratory_rate_min must be positive")

        rox = (spo2 / fio2) / rate
        results.append({
            "hours": hours,
            "spo2_percent": spo2,
            "fio2_fraction": fio2,
            "respiratory_rate_min": rate,
            "rox": rox,
            "original_pneumonia_cohort_zone": _classify(hours, rox),
        })

    trend = None
    if len(results) > 1:
        difference = results[-1]["rox"] - results[0]["rox"]
        trend = {
            "absolute_change_first_to_last": difference,
            "direction": "rising" if difference > 0 else
                         "falling" if difference < 0 else "unchanged",
        }

    return {
        "observations": results,
        "trend": trend,
        "safety": (
            "ROX is an adjunct validated originally in adults with pneumonia. "
            "It must not delay intubation when oxygenation, work of breathing, "
            "mental status, hemodynamics, ventilation or airway protection worsen."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_input", nargs="?", help="JSON object; defaults to stdin")
    args = parser.parse_args()
    payload = json.loads(args.json_input) if args.json_input else json.load(sys.stdin)
    print(json.dumps(calculate(payload), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
