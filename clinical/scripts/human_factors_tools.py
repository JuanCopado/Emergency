#!/usr/bin/env python3
"""R14/R15 · tooling for the R5-1 human-factors evaluation (policy layer 8). Standard library only.

The planned study repeats trials within each professional and is crossed (every participant works
under both conditions), so the trials of one participant are NOT independent. The main analysis is
therefore a cluster bootstrap that resamples PARTICIPANTS, keeps all of a participant's trials
together and evaluates both conditions on the same resampled participants (so the pairing survives).
Wilson and Clopper-Pearson intervals assume independent trials; they are kept only as a clearly
labelled DESCRIPTIVE exploration and must not be used for inference.

It has NO file-system access (standard input in, standard output out; a test fails if the module ever
opens a file). Records admit no free text: only closed values and pseudonymous codes, so no personal
data can enter. Synthetic images only. It measures a user-interface behaviour, not clinical
performance, sets no acceptance margin (a medical decision) and does not mean that the study has run.
"""
import argparse
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict

MODALITIES = ("skin_wound", "ecg", "xray", "pocus", "document")
ROLES = ("physician", "nurse", "paramedic", "other_professional")
CONDITIONS = ("baseline", "prototype")
PERIODS = (1, 2)
CODE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
FIELDS = {"participant", "role", "scenario_id", "condition", "period", "intended_modality", "initial_modality",
          "chosen_modality", "confirmed", "changed_modality_count", "seconds", "comprehension_correct"}
SKIN = "skin_wound"
DEFAULT_RESAMPLES = 2000
DESCRIPTIVE_NOTE = ("Wilson and Clopper-Pearson assume independent trials; the trials of one participant are not. "
                    "Descriptive only, never for inference. The main analysis is the cluster bootstrap.")

# Metric name -> (numerator flag, denominator flag), both derived from the record; none is trusted from input.
METRICS = {
    "bypass_rate": ("bypass", "intended_skin"),                  # skin photo confirmed under another modality
    "confirmation_error_rate": ("confirmation_error", "any"),    # a wrong modality was confirmed
    "false_cancellation_rate": ("false_cancellation", "initial_correct"),  # a correct first choice was dropped
    "comprehension_rate": ("comprehension_correct", "comprehension_answered"),
}


def _is_count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_records(records):
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty list")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != FIELDS:
            raise ValueError(f"record fields must be exactly {sorted(FIELDS)}")
        for field in ("participant", "scenario_id"):
            if not isinstance(record[field], str) or not CODE.match(record[field]):
                raise ValueError(f"{field} must be a pseudonymous code (letters, digits, - and _ only)")
        if record["role"] not in ROLES or record["condition"] not in CONDITIONS or record["period"] not in PERIODS:
            raise ValueError("unknown role, condition or period")
        if isinstance(record["period"], bool):
            raise ValueError("period must be 1 or 2")
        if record["intended_modality"] not in MODALITIES:
            raise ValueError("unknown intended modality")
        for field in ("initial_modality", "chosen_modality"):
            if record[field] is not None and record[field] not in MODALITIES:
                raise ValueError(f"unknown {field}")
        if not isinstance(record["confirmed"], bool):
            raise ValueError("confirmed must be a boolean")
        if record["confirmed"] and record["chosen_modality"] is None:
            raise ValueError("a confirmed record needs a chosen modality")
        if not _is_count(record["changed_modality_count"]):
            raise ValueError("changed_modality_count must be a non-negative integer")
        seconds = record["seconds"]
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds < 0:
            raise ValueError("seconds must be a finite non-negative number")
        if record["comprehension_correct"] is not None and not isinstance(record["comprehension_correct"], bool):
            raise ValueError("comprehension_correct must be true, false or null")
        key = (record["participant"], record["scenario_id"], record["condition"])
        if key in seen:
            raise ValueError(f"participant {key[0]} has scenario {key[1]} twice under {key[2]}")
        seen.add(key)
    return True


def flags(record):
    """Per-trial outcome flags, all derived from the closed fields (nothing is trusted from the input)."""
    intended, initial, chosen = record["intended_modality"], record["initial_modality"], record["chosen_modality"]
    wrong_confirmed = record["confirmed"] and chosen != intended
    return {
        "any": True,
        "intended_skin": intended == SKIN,
        "confirmation_error": wrong_confirmed,
        "bypass": wrong_confirmed and intended == SKIN,
        "initial_correct": initial == intended,
        "false_cancellation": initial == intended and chosen != intended,
        "comprehension_answered": record["comprehension_correct"] is not None,
        "comprehension_correct": record["comprehension_correct"] is True,
    }


def clusters(records):
    """Group trials by participant (the unit of resampling)."""
    grouped = defaultdict(list)
    for record in records:
        grouped[record["participant"]].append(record)
    return grouped


def tally(trials):
    """Per (condition, group) counts for ONE participant; every later estimate is a ratio of summed counts."""
    cells = defaultdict(Counter)
    for trial in trials:
        derived = flags(trial)
        for group in (("all",), ("modality", trial["intended_modality"]), ("scenario", trial["scenario_id"])):
            cell = cells[(trial["condition"], group)]
            cell["trials"] += 1
            cell["seconds"] += trial["seconds"]
            for metric, (numerator, denominator) in METRICS.items():
                if derived[denominator]:
                    cell[metric + ":den"] += 1
                    cell[metric + ":num"] += int(derived[numerator])
    return cells


def total(tables, drawn, key):
    """Sum the counts of the drawn participants (a participant drawn twice counts twice, with ALL its trials)."""
    summed = Counter()
    for participant in drawn:
        summed.update(tables[participant].get(key, Counter()))
    return summed


def rate(cell, metric):
    denominator = cell[metric + ":den"]
    return cell[metric + ":num"] / denominator if denominator else None


def mean_seconds(cell):
    return cell["seconds"] / cell["trials"] if cell["trials"] else None


def cluster_resample(cluster_ids, rng):
    """Draw participants with replacement; the same draw is used for every condition (pairing preserved)."""
    return [cluster_ids[rng.randrange(len(cluster_ids))] for _ in cluster_ids]


def _percentile(sorted_values, q):
    position = q * (len(sorted_values) - 1)
    low, high = math.floor(position), math.ceil(position)
    return sorted_values[low] + (sorted_values[high] - sorted_values[low]) * (position - low)


def _interval(values):
    kept = sorted(v for v in values if v is not None)
    if len(kept) < 2:
        return None
    return [round(_percentile(kept, 0.025), 4), round(_percentile(kept, 0.975), 4)]


def _rounded(value, places=4):
    return None if value is None else round(value, places)


def wilson(k, n, z=1.959964):
    if n <= 0:
        return None
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def _pmf(i, n, p):
    """Binomial probability mass; only the bisection calls it, always with 0 < p < 1."""
    log_comb = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
    return math.exp(log_comb + i * math.log(p) + (n - i) * math.log1p(-p))


def _tail_ge(k, n, p):
    return sum(_pmf(i, n, p) for i in range(k, n + 1))


def _tail_le(k, n, p):
    return sum(_pmf(i, n, p) for i in range(0, k + 1))


def clopper_pearson(k, n, alpha=0.05):
    """Exact interval for a binomial proportion of INDEPENDENT trials (descriptive use only)."""
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


def _descriptive(trials, metric):
    numerator_flag, denominator_flag = METRICS[metric]
    n = sum(flags(t)[denominator_flag] for t in trials)
    k = sum(flags(t)[numerator_flag] and flags(t)[denominator_flag] for t in trials)
    ci, wi = clopper_pearson(k, n), wilson(k, n)
    return {"events": k, "trials": n, "exact_95": [round(x, 4) for x in ci] if ci else None,
            "wilson_95": [round(x, 4) for x in wi] if wi else None}


def _estimate(tables, drawn, key, measure):
    return measure(total(tables, drawn, key))


def _bootstrap(tables, ids, resamples, rng, estimator):
    """Point estimate on the real participants plus the percentile interval over participant resamples."""
    point = estimator(ids)
    samples = [estimator(cluster_resample(ids, rng)) for _ in range(resamples)] if len(ids) >= 2 else []
    return {"estimate": _rounded(point), "cluster_bootstrap_95": _interval(samples)}


def summarize(records, resamples=DEFAULT_RESAMPLES, seed="r15"):
    validate_records(records)
    grouped = clusters(records)
    ids = sorted(grouped)
    tables = {p: tally(trials) for p, trials in grouped.items()}
    rng = random.Random(f"{seed}:{len(ids)}")
    both = {p for p in ids if {t["condition"] for t in grouped[p]} == set(CONDITIONS)}
    both_ids = sorted(both)
    scenarios = sorted({t["scenario_id"] for t in records})
    modalities = [m for m in MODALITIES if any(t["intended_modality"] == m for t in records)]

    def cell(metric, condition, group):
        return _bootstrap(tables, ids, resamples, rng,
                          lambda drawn: _estimate(tables, drawn, (condition, group), lambda c: rate(c, metric)))

    def paired(measure, group):
        def estimator(drawn):
            kept = [p for p in drawn if p in both]
            proto = _estimate(tables, kept, ("prototype", group), measure)
            base = _estimate(tables, kept, ("baseline", group), measure)
            return None if proto is None or base is None else proto - base
        return _bootstrap(tables, both_ids, resamples, rng, estimator)

    def rates(metric):
        return lambda c: rate(c, metric)

    return {
        "design": {"unit_of_analysis": "participant", "trials": len(records), "participants": len(ids),
                   "participants_with_both_conditions": len(both_ids), "paired": True, "resamples": resamples if len(ids) >= 2 else 0,
                   "seed": str(seed), "trials_per_condition_and_period": dict(Counter(f"{t['condition']}@period{t['period']}" for t in records)),
                   "independence_of_trials": "NOT_ASSUMED"},
        "primary_cluster_bootstrap": {
            "by_condition": {c: {m: cell(m, c, ("all",)) for m in METRICS} for c in CONDITIONS},
            "by_condition_and_modality": {c: {mod: {m: cell(m, c, ("modality", mod)) for m in METRICS} for mod in modalities} for c in CONDITIONS},
            "by_condition_and_scenario": {c: {s: {m: cell(m, c, ("scenario", s)) for m in METRICS} for s in scenarios} for c in CONDITIONS},
            "paired_difference_prototype_minus_baseline": {m: paired(rates(m), ("all",)) for m in METRICS},
            "paired_difference_by_modality": {mod: {m: paired(rates(m), ("modality", mod)) for m in METRICS} for mod in modalities},
            "additional_time_seconds_prototype_minus_baseline": paired(mean_seconds, ("all",)),
        },
        "by_participant": {p: {c: {"trials": tables[p].get((c, ("all",)), Counter())["trials"],
                                   **{m: _rounded(rate(tables[p].get((c, ("all",)), Counter()), m)) for m in METRICS}}
                               for c in CONDITIONS} for p in ids},
        "descriptive_exploration_only": {"note": DESCRIPTIVE_NOTE,
                                         "by_condition": {c: {m: _descriptive([t for t in records if t["condition"] == c], m) for m in METRICS}
                                                          for c in CONDITIONS}},
        "acceptance_margin": "NOT_SET_MEDICAL_DECISION",
        "study_status": "NOT_EXECUTED_TOOLING_ONLY",
    }


def run(argv, raw):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("validate", "summarize"), help="stdin: JSON list of trial records")
    parser.add_argument("--resamples", type=int, default=DEFAULT_RESAMPLES)
    parser.add_argument("--seed", default="r15")
    args = parser.parse_args(argv)
    records = json.loads(raw.decode("utf-8"))
    if args.command == "validate":
        validate_records(records)
        return {"valid": True, "records": len(records)}
    return summarize(records, args.resamples, args.seed)


def main(argv=None):
    result = run(sys.argv[1:] if argv is None else argv, sys.stdin.buffer.read())
    sys.stdout.write(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
