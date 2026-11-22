#!/usr/bin/env python3
"""R14 · tooling for the R5-1 human-factors evaluation (policy layer 8). Standard library only.

Validates session records and summarises the residual human error of choosing a modality, with exact
(Clopper-Pearson) and Wilson 95 % intervals. It has NO file-system access: input arrives on standard
input and output goes to standard output, and a test fails if the module ever opens a file. Records
admit no free text (only closed values and opaque codes), so no patient data can enter. Synthetic
images only. It measures a user-interface behaviour, not clinical performance, and sets no
acceptance threshold: that is a medical decision.
"""
import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict

MODALITIES = ("skin_wound", "ecg", "xray", "pocus", "document")
ROLES = ("physician", "nurse", "paramedic", "other_professional")
OUTCOMES = ("correct", "wrong_modality", "abandoned", "timeout")
CODE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
FIELDS = {"participant", "role", "task_id", "intended_modality", "chosen_modality",
          "changed_modality_count", "outcome", "seconds"}


def validate_records(records):
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError(f"record fields must be exactly {sorted(FIELDS)}")
        for field in ("participant", "task_id"):
            if not isinstance(record[field], str) or not CODE.match(record[field]):
                raise ValueError(f"{field} must be an opaque code (letters, digits, - and _ only)")
        if record["role"] not in ROLES or record["outcome"] not in OUTCOMES:
            raise ValueError("unknown role or outcome")
        if record["intended_modality"] not in MODALITIES:
            raise ValueError("unknown intended modality")
        chosen = record["chosen_modality"]
        if chosen is not None and chosen not in MODALITIES:
            raise ValueError("unknown chosen modality")
        count = record["changed_modality_count"]
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError("changed_modality_count must be a non-negative integer")
        seconds = record["seconds"]
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be a finite non-negative number")
        if record["outcome"] == "correct" and chosen != record["intended_modality"]:
            raise ValueError("outcome correct requires chosen == intended")
        if record["outcome"] == "wrong_modality" and (chosen is None or chosen == record["intended_modality"]):
            raise ValueError("outcome wrong_modality requires a different chosen modality")
        pair = (record["participant"], record["task_id"])
        if pair in seen:
            raise ValueError(f"participant {pair[0]} has task {pair[1]} twice")
        seen.add(pair)
    return True


def wilson(k, n, z=1.959964):
    if n <= 0:
        return None
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def _pmf(i, n, p):
    if p <= 0:
        return 1.0 if i == 0 else 0.0
    if p >= 1:
        return 1.0 if i == n else 0.0
    log_comb = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
    return math.exp(log_comb + i * math.log(p) + (n - i) * math.log1p(-p))


def _tail_ge(k, n, p):
    return sum(_pmf(i, n, p) for i in range(k, n + 1))


def _tail_le(k, n, p):
    return sum(_pmf(i, n, p) for i in range(0, k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided interval for a binomial proportion, by bisection on the binomial tails."""
    if n <= 0 or not 0 <= k <= n:
        return None

    def bisect(predicate):
        low, high = 0.0, 1.0
        for _ in range(100):
            mid = (low + high) / 2
            low, high = (mid, high) if predicate(mid) else (low, mid)
        return (low + high) / 2

    lower = 0.0 if k == 0 else bisect(lambda p: _tail_ge(k, n, p) < alpha / 2)
    upper = 1.0 if k == n else bisect(lambda p: _tail_le(k, n, p) > alpha / 2)
    return lower, upper


def _rate(k, n):
    ci = clopper_pearson(k, n)
    wi = wilson(k, n)
    return {"n": n, "wrong_modality": k, "rate": k / n if n else None,
            "exact_95": [round(x, 4) for x in ci] if ci else None,
            "wilson_95": [round(x, 4) for x in wi] if wi else None}


def summarize(records):
    validate_records(records)
    by_modality = defaultdict(lambda: [0, 0])
    for record in records:
        cell = by_modality[record["intended_modality"]]
        cell[0] += 1
        cell[1] += record["outcome"] == "wrong_modality"
    total_wrong = sum(cell[1] for cell in by_modality.values())
    return {
        "records": len(records),
        "participants": len({r["participant"] for r in records}),
        "outcomes": dict(Counter(r["outcome"] for r in records)),
        "residual_human_error": _rate(total_wrong, len(records)),
        "by_intended_modality": {m: _rate(by_modality[m][1], by_modality[m][0]) for m in MODALITIES if by_modality[m][0]},
        "changed_modality": {"sessions_with_a_change": sum(r["changed_modality_count"] > 0 for r in records)},
        "acceptance_threshold": "NOT_SET_MEDICAL_DECISION",
    }


def run(argv, raw):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("validate", "summarize"), help="stdin: JSON list of session records")
    args = parser.parse_args(argv)
    records = json.loads(raw.decode("utf-8"))
    if args.command == "validate":
        validate_records(records)
        return {"valid": True, "records": len(records)}
    return summarize(records)


def main(argv=None):
    result = run(sys.argv[1:] if argv is None else argv, sys.stdin.buffer.read())
    sys.stdout.write(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
