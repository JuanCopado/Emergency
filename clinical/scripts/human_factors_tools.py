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
import hashlib
import json
import math
import random
import re
import statistics
import sys
from collections import Counter, defaultdict

MODALITIES = ("skin_wound", "ecg", "xray", "pocus", "document")
ROLES = ("physician", "nurse", "paramedic", "other_professional")
CONDITIONS = ("baseline", "prototype")
PERIODS = (1, 2)
PLATFORMS = ("web", "mobile")
CODE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
FIELDS = {"participant", "role", "scenario_id", "condition", "period", "intended_modality", "initial_modality",
          "chosen_modality", "confirmed", "changed_modality_count", "seconds", "comprehension_correct",
          "platform", "order_in_period"}
SKIN = "skin_wound"
DEFAULT_RESAMPLES = 5000
LIMITATIONS = (
    "No sample size and no acceptance margin are set here: both are medical/study-design decisions.",
    "Percentile bootstrap intervals can undercover when the number of participants is small; read them with the participant count.",
    "A bootstrap interval over participants with zero observed events is degenerate and is not reported as evidence of zero risk.",
    "Learning is estimated from the order of trials inside a period and is confounded with scenario difficulty unless scenarios are counterbalanced.",
    "Web and mobile are compared descriptively; platform is not assumed to be randomised.",
)
DESCRIPTIVE_NOTE = ("Wilson and Clopper-Pearson assume independent trials; the trials of one participant are not. "
                    "Descriptive only, never for inference. The main analysis is the cluster bootstrap.")

# Metric name -> (numerator flag, denominator flag), both derived from the record; none is trusted from input.
METRICS = {
    "bypass_rate": ("bypass", "intended_skin"),                  # skin photo confirmed under another modality
    "confirmation_error_rate": ("confirmation_error", "any"),    # a wrong modality was confirmed
    "false_cancellation_rate": ("false_cancellation", "initial_correct"),  # a correct first choice was dropped
    "comprehension_rate": ("comprehension_correct", "comprehension_answered"),
}
# Participant-level risk is only defined for the error-type events (at least one in the participant's trials).
PARTICIPANT_METRICS = ("bypass_rate", "confirmation_error_rate", "false_cancellation_rate")


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
        if record["platform"] not in PLATFORMS:
            raise ValueError("platform must be web or mobile")
        if not _is_count(record["order_in_period"]) or record["order_in_period"] < 1 or isinstance(record["order_in_period"], bool):
            raise ValueError("order_in_period must be a positive integer")
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
    _check_crossed_periods(records)
    return len(records)


def _check_crossed_periods(records):
    """In a crossed AB/BA design a participant uses ONE condition per period (never both in the same period)."""
    used = defaultdict(set)
    for record in records:
        used[(record["participant"], record["period"])].add(record["condition"])
    for (participant, period), conditions in used.items():
        if len(conditions) > 1:
            raise ValueError(f"participant {participant} mixes conditions inside period {period}")


def sequences(records):
    """Participant -> 'AB' (baseline first), 'BA' (prototype first) or 'single' (only one condition observed)."""
    first = {}
    conditions = defaultdict(set)
    for record in records:
        participant = record["participant"]
        conditions[participant].add(record["condition"])
        if participant not in first or record["period"] < first[participant][0]:
            first[participant] = (record["period"], record["condition"])
    return {p: ("single" if len(conditions[p]) < 2 else ("AB" if first[p][1] == "baseline" else "BA")) for p in first}


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


def tally(trials, median_order=None):
    """Per (condition, group) counts for ONE participant; every later estimate is a ratio of summed counts."""
    cells = defaultdict(Counter)
    for trial in trials:
        derived = flags(trial)
        groups = [("all",), ("modality", trial["intended_modality"]), ("scenario", trial["scenario_id"]),
                  ("platform", trial["platform"]), ("period", trial["period"])]
        if median_order is not None:
            groups.append(("order", "early" if trial["order_in_period"] <= median_order else "late"))
        for group in groups:
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


def cluster_resample(cluster_ids, rng, strata=None):
    """Draw participants with replacement; the same draw is used for every condition (pairing preserved).

    With `strata` (participant -> sequence) the draw is made inside each stratum, so every resample keeps
    the AB/BA balance of the real sample."""
    if not strata:
        return [cluster_ids[rng.randrange(len(cluster_ids))] for _ in cluster_ids]
    drawn = []
    for stratum in sorted({strata[c] for c in cluster_ids}):
        members = [c for c in cluster_ids if strata[c] == stratum]
        drawn.extend(members[rng.randrange(len(members))] for _ in members)
    return drawn


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


ZERO_EVENTS_NOTE = ("No event observed: report the exact upper bound (about 3/n for n independent trials), "
                    "never 'zero risk'; with clustered data the bound is optimistic.")
DEGENERATE_NOTE = ("No variation across resamples (for example zero events in every participant): the interval "
                   "is degenerate and is not evidence of zero risk.")


def _descriptive(trials, metric):
    numerator_flag, denominator_flag = METRICS[metric]
    n = sum(flags(t)[denominator_flag] for t in trials)
    k = sum(flags(t)[numerator_flag] and flags(t)[denominator_flag] for t in trials)
    ci, wi = clopper_pearson(k, n), wilson(k, n)
    return {"events": k, "trials": n, "exact_95": [round(x, 4) for x in ci] if ci else None,
            "wilson_95": [round(x, 4) for x in wi] if wi else None,
            "zero_events_note": ZERO_EVENTS_NOTE if k == 0 and n > 0 else None}


def _estimate(tables, drawn, key, measure):
    return measure(total(tables, drawn, key))


BCA_MIN_PARTICIPANTS = 20       # R23 protocol: BCa only with at least 20 participants in the estimand ...
BCA_MIN_WITH_EVENT = 2          # ... and at least 2 participants with events
BCA_MIN_WITHOUT_EVENT = 2       # ... and at least 2 without events
VERY_SMALL_CLUSTER = 16         # R23 protocol: below this the intervals are descriptive only
BCA_FALLBACK = "FALLBACK_SMALL_SAMPLE_OR_DEGENERATE"
SMALL_CLUSTER_REFERENCE = 30   # literature reference for stable cluster-bootstrap coverage (Deen & de Rooij 2020), not a study threshold
NORMAL = statistics.NormalDist()


def _quantile(sorted_values, q):
    return _percentile(sorted_values, min(max(q, 0.0), 1.0))


BCA_MIN_PER_SEQUENCE = 8        # C2: each AB/BA stratum must hold >= 8 participants of the estimand (P >= 20 overall, C1).
                                # Value as cited by the owner from the Gemini R26/R27 specification (PR94 coordination comment);
                                # the literal Gemini text was not received by this tool: source status below, not a clinical decision.
BCA_C2_THRESHOLD_STATUS = "OWNER_CITED_GEMINI_R26_R27_SPEC_LITERAL_NOT_RECEIVED"
BCA_JACKKNIFE_SS_MIN = 1e-12    # C4: jackknife sum of squares must exceed this; otherwise the acceleration is undefined


def _bca_diagnosed(point, samples, jackknife):
    """Bias-corrected and accelerated interval from bootstrap samples and leave-one-participant-out values.

    Returns (bounds | None, diagnostics). Nothing is silently replaced (C4): a degenerate bias correction, a null jackknife
    variance (undefined acceleration), a non-positive denominator or an adjusted quantile outside (0, 1) withholds the interval
    and says why, so the caller reports the cluster percentile interval instead."""
    observed = sorted(v for v in samples if v is not None)
    leave_out = [v for v in jackknife if v is not None]
    diag = {"z0": None, "acceleration": None, "adjusted_alphas": None, "failure": None}
    if point is None or len(observed) < 2 or len(leave_out) < 2:
        diag["failure"] = "insufficient_bootstrap_or_jackknife_values"
        return None, diag
    below = sum(v < point for v in observed) / len(observed)
    if below <= 0.0 or below >= 1.0:
        diag["failure"] = "bias_correction_degenerate"                  # z0 would be infinite
        return None, diag
    z0 = NORMAL.inv_cdf(below)
    mean = sum(leave_out) / len(leave_out)
    cubes = sum((mean - v) ** 3 for v in leave_out)
    squares = sum((mean - v) ** 2 for v in leave_out)
    if squares <= BCA_JACKKNIFE_SS_MIN:
        diag.update(z0=round(z0, 6), failure="acceleration_undefined_null_jackknife_variance")
        return None, diag
    acceleration = cubes / (6 * squares ** 1.5)
    diag.update(z0=round(z0, 6), acceleration=round(acceleration, 6))
    bounds, alphas = [], []
    for alpha in (0.025, 0.975):
        z = NORMAL.inv_cdf(alpha)
        denominator = 1 - acceleration * (z0 + z)
        if denominator <= 0:
            diag["failure"] = "adjusted_quantile_denominator_not_positive"
            return None, diag
        adjusted = NORMAL.cdf(z0 + (z0 + z) / denominator)
        resamples = len(samples)
        if not math.isfinite(adjusted) or not 1.0 / resamples <= adjusted <= 1.0 - 1.0 / resamples:
            diag["failure"] = "adjusted_quantile_invalid"           # C4: alpha must lie in [1/B, 1-1/B]; never clamped
            return None, diag
        alphas.append(round(adjusted, 6))
        bounds.append(round(_quantile(observed, adjusted), 4))
    if not alphas[0] < alphas[1]:
        diag["failure"] = "adjusted_quantiles_not_ordered"
        return None, diag
    diag["adjusted_alphas"] = alphas
    return bounds, diag


def _bca(point, samples, jackknife):
    """Historical interface (bounds or None); the diagnosed variant explains every refusal."""
    return _bca_diagnosed(point, samples, jackknife)[0]


WILCOXON_TOLERANCE = 1e-12   # differences closer than this are one value (no float equality tests); seconds-scale data


def wilcoxon_signed_rank(differences):
    """Paired Wilcoxon signed-rank test on PARTICIPANT-level differences (one value per participant, prototype minus baseline).

    Method (declared, not inferred): zero differences are dropped (Wilcoxon convention); tied absolute differences receive average
    ranks. With n <= 25 non-zero differences the two-sided p-value is EXACT (dynamic-programming count of the sign-permutation null
    distribution of W+ over the actual ranks; with ties it is the conditional permutation p, labelled). With n > 25 it is APPROXIMATE: normal approximation with tie-corrected variance and continuity
    correction, labelled as such. Formative use only; never an A/B inference for M2."""
    values = [float(d) for d in differences if d is not None]
    if any(not math.isfinite(v) for v in values):
        raise ValueError("non-finite difference")
    nonzero = [v for v in values if not math.isclose(v, 0.0, rel_tol=0.0, abs_tol=WILCOXON_TOLERANCE)]
    n = len(nonzero)
    out = {"method": "wilcoxon_signed_rank_participant_level", "n_participants": len(values), "n_zero_dropped": len(values) - n, "n_effective": n}
    if n == 0:
        return {**out, "w_plus": None, "w_minus": None, "p_value_two_sided": None, "p_value_kind": "NOT_COMPUTABLE_NO_NONZERO_DIFFERENCES", "ties": False}
    order = sorted(range(n), key=lambda i: abs(nonzero[i]))
    ranks, i, tie_groups = [0.0] * n, 0, []
    while i < n:
        j = i
        while j + 1 < n and math.isclose(abs(nonzero[order[j + 1]]), abs(nonzero[order[i]]), rel_tol=0.0, abs_tol=WILCOXON_TOLERANCE):
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        tie_groups.append(j - i + 1)
        i = j + 1
    w_plus = sum(r for r, v in zip(ranks, nonzero) if v > 0)
    w_minus = sum(r for r, v in zip(ranks, nonzero) if v < 0)
    ties = any(t > 1 for t in tie_groups)
    total = n * (n + 1) / 2
    out.update(w_plus=w_plus, w_minus=w_minus, ties=ties)
    if n <= 25:
        doubled = [int(round(2 * r)) for r in ranks]                    # average ranks are multiples of 0.5: exact integer arithmetic
        counts = [0] * (sum(doubled) + 1)
        counts[0] = 1
        for r in doubled:
            for w in range(len(counts) - 1, r - 1, -1):
                counts[w] += counts[w - r]
        smaller = int(round(2 * min(w_plus, w_minus)))
        tail = sum(counts[: smaller + 1]) / 2 ** n
        out.update(p_value_two_sided=min(1.0, 2 * tail), p_value_kind="EXACT_PERMUTATION_AVERAGE_RANKS" if ties else "EXACT_NO_TIES")
        return out
    mean = total / 2
    variance = n * (n + 1) * (2 * n + 1) / 24 - sum(t ** 3 - t for t in tie_groups) / 48
    if variance <= 0:
        return {**out, "p_value_two_sided": None, "p_value_kind": "NOT_COMPUTABLE_ZERO_VARIANCE"}
    z = (abs(w_plus - mean) - 0.5) / math.sqrt(variance)
    out.update(p_value_two_sided=min(1.0, 2 * (1 - NORMAL.cdf(max(z, 0.0)))), p_value_kind="APPROXIMATE_NORMAL_TIE_CORRECTED_CONTINUITY")
    return out


def _bootstrap(ids, resamples, rng, estimator, strata=None, event_flags=None):
    """Point estimate on the real participants plus percentile and (when admissible) BCa intervals over participant resamples.

    `event_flags` (participant -> had at least one event) describes the participants that contribute to THIS estimand; when
    given, the participant count and the with/without-event counts come from it. BCa is the primary interval only with
    >= 20 participants, >= 2 with and >= 2 without events and a non-degenerate bootstrap; otherwise it is withheld
    (bca_status FALLBACK_SMALL_SAMPLE_OR_DEGENERATE) and the cluster percentile interval is reported."""
    participants = len(event_flags) if event_flags is not None else len(ids)
    with_event = sum(event_flags.values()) if event_flags is not None else None
    without_event = participants - with_event if event_flags is not None else None
    point = estimator(ids)
    samples = [estimator(cluster_resample(ids, rng, strata)) for _ in range(resamples)] if len(ids) >= 2 else []
    observed = [v for v in samples if v is not None]
    degenerate = len(observed) >= 2 and len(set(observed)) == 1
    c1 = participants >= BCA_MIN_PARTICIPANTS
    if strata:
        per_stratum = Counter(strata[c] for c in ids)
        c2 = len(per_stratum) >= 2 and all(n >= BCA_MIN_PER_SEQUENCE for n in per_stratum.values())
    else:
        c2 = None                                                       # not a crossed estimand: no sequence strata
    c3 = (not degenerate and len(ids) >= 3 and bool(samples)
          and (event_flags is None or (with_event >= BCA_MIN_WITH_EVENT and without_event >= BCA_MIN_WITHOUT_EVENT)))
    bca_admissible = c1 and c3 and c2 is not False
    bca, bca_parameters, c4 = None, None, None
    if bca_admissible:
        jackknife = [estimator([x for x in ids if x != left]) for left in ids]
        bca, bca_parameters = _bca_diagnosed(point, samples, jackknife)
        c4 = bca is not None
    conditions = {"C1_min_participants": c1, "C2_sequences_represented": c2, "C3_variation_and_events": c3, "C4_parameters_valid": c4}
    conditions["failed"] = [k for k in ("C1_min_participants", "C2_sequences_represented", "C3_variation_and_events",
                                        "C4_parameters_valid") if conditions[k] is False]
    percentile = None if degenerate else _interval(samples)
    if bca:
        primary, status = "bca", "BCA_PRIMARY"
    else:
        primary = "percentile" if percentile else None
        status = BCA_FALLBACK if not bca_admissible else "BCA_NOT_COMPUTABLE"
    se = _rounded(statistics.pstdev(observed)) if len(observed) >= 2 and not degenerate else None   # plug-in SE over replicates
    return {"estimate": _rounded(point), "cluster_bootstrap_95": percentile, "cluster_bootstrap_se": se,
            "cluster_bootstrap_bca_95": bca, "primary_interval": primary, "bca_status": status,
            "bca_conditions": conditions, "bca_parameters": bca_parameters,
            "participants_in_estimand": participants, "participants_with_event": with_event, "participants_without_event": without_event,
            "small_cluster_warning": participants < SMALL_CLUSTER_REFERENCE,
            "very_small_cluster_descriptive_only": participants < VERY_SMALL_CLUSTER,
            "degenerate_interval": degenerate, "zero_event_degeneracy_flag": degenerate,
            "note": DEGENERATE_NOTE if degenerate else None}


def _binom_cdf(k, n, p=0.5):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from the discordant pairs (exploratory; never an acceptance verdict)."""
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * _binom_cdf(min(b, c), n))


def icc_anova(clusters):
    """One-way ANOVA intraclass correlation of binary outcomes for clusters of (events, trials); None if undefined."""
    sizes = [m for _, m in clusters if m > 0]
    k, total = len(sizes), sum(sizes)
    if k < 2 or total <= k:
        return None
    ordered = [(e, m) for e, m in clusters if m > 0]
    grand = sum(e for e, _ in ordered) / total
    between = sum(m * (e / m - grand) ** 2 for e, m in ordered) / (k - 1)
    within = sum(e * (1 - e / m) for e, m in ordered) / (total - k)   # sum over trials of (y - cluster mean)^2 for binary y
    m0 = (total - sum(m * m for m in sizes) / total) / (k - 1)
    denominator = between + (m0 - 1) * within
    return None if denominator <= 0 else (between - within) / denominator


def zero_event_report(events, trials, participants_with_events, participants):
    if events != 0 or trials <= 0 or participants <= 0:
        return None
    return {"events_over_trials": f"0/{trials}", "participants_with_event_over_participants": f"0/{participants}",
            "participant_risk_upper_95_one_sided": round(1 - 0.05 ** (1 / participants), 4),
            "participant_risk_upper_95_two_sided": round(1 - 0.025 ** (1 / participants), 4),
            "label": "upper bound of the participant-level risk P(Y_i >= 1); a worst-case envelope for the trial rate, never an exact trial-rate interval",
            "forbidden": "Clopper-Pearson or Wilson over 0/N trials (assumes rho = 0)"}


def _participant_cell(tables, p, condition, metric):
    return tables[p].get((condition, ("all",)), Counter())


def summarize(records, resamples=DEFAULT_RESAMPLES, seed="r15"):
    validate_records(records)
    grouped = clusters(records)
    ids = sorted(grouped)
    strata = sequences(records)
    orders = sorted(t["order_in_period"] for t in records)
    median_order = orders[(len(orders) - 1) // 2]
    tables = {p: tally(trials, median_order) for p, trials in grouped.items()}
    rng = random.Random(f"{seed}:{len(ids)}")
    both = {p for p in ids if {t["condition"] for t in grouped[p]} == set(CONDITIONS)}
    both_ids = sorted(both)
    scenarios = sorted({t["scenario_id"] for t in records})
    modalities = [m for m in MODALITIES if any(t["intended_modality"] == m for t in records)]
    platforms = [pl for pl in PLATFORMS if any(t["platform"] == pl for t in records)]

    def boot(pool, estimator, flags_=None):
        return _bootstrap(pool, resamples, rng, estimator, strata, flags_)

    def profile(pool, metric, key_sets):
        """participant -> had an event, for the participants that are eligible in EVERY key set of this estimand."""
        out = {}
        for p in pool:
            sums = []
            for keys in key_sets:
                acc = Counter()
                for key in keys:
                    acc.update(tables[p].get(key, Counter()))
                sums.append(acc)
            if all(c[metric + ":den"] > 0 for c in sums):
                out[p] = any(c[metric + ":num"] > 0 for c in sums)
        return out

    def cell(metric, condition, group):
        return boot(ids, lambda drawn: _estimate(tables, drawn, (condition, group), lambda c: rate(c, metric)),
                    profile(ids, metric, [[(condition, group)]]))

    def paired(measure, group, metric=None):
        def estimator(drawn):
            kept = [p for p in drawn if p in both]
            proto = _estimate(tables, kept, ("prototype", group), measure)
            base = _estimate(tables, kept, ("baseline", group), measure)
            return None if proto is None or base is None else proto - base
        flags_ = profile(both_ids, metric, [[("prototype", group)], [("baseline", group)]]) if metric else None
        return boot(both_ids, estimator, flags_)

    def rates(metric):
        return lambda c: rate(c, metric)

    def share_with_event(drawn, condition, metric):
        eligible = [p for p in drawn if _participant_cell(tables, p, condition, metric)[metric + ":den"] > 0]
        if not eligible:
            return None
        return sum(_participant_cell(tables, p, condition, metric)[metric + ":num"] > 0 for p in eligible) / len(eligible)

    def participant_cell(metric, condition):
        return boot(ids, lambda drawn: share_with_event(drawn, condition, metric), profile(ids, metric, [[(condition, ("all",))]]))

    def participant_paired(metric):
        def estimator(drawn):
            kept = [p for p in drawn if p in both]
            proto, base = share_with_event(kept, "prototype", metric), share_with_event(kept, "baseline", metric)
            return None if proto is None or base is None else proto - base
        return boot(both_ids, estimator, profile(both_ids, metric, [[("prototype", ("all",))], [("baseline", ("all",))]]))

    def pooled_rate(metric, group):
        def estimator(drawn):
            summed = Counter()
            for condition in CONDITIONS:
                summed.update(total(tables, drawn, (condition, group)))
            return rate(summed, metric)
        return estimator

    def contrast(metric, late_group, early_group):
        def estimator(drawn):
            late, early = pooled_rate(metric, late_group)(drawn), pooled_rate(metric, early_group)(drawn)
            return None if late is None or early is None else late - early
        return boot(ids, estimator, profile(ids, metric, [[(c, late_group) for c in CONDITIONS], [(c, early_group) for c in CONDITIONS]]))

    def eligible_counts(condition, metric):
        cells = [_participant_cell(tables, q, condition, metric) for q in ids]
        eligible = [c for c in cells if c[metric + ":den"] > 0]
        return eligible, sum(c[metric + ":num"] > 0 for c in eligible)

    def participant_exact(condition, metric):
        eligible, with_event = eligible_counts(condition, metric)
        interval = clopper_pearson(with_event, len(eligible))
        report = zero_event_report(sum(c[metric + ":num"] for c in eligible), sum(c[metric + ":den"] for c in eligible),
                                   with_event, len(eligible))
        return {"participants": len(eligible), "with_event": with_event,
                "exact_95_over_participants": [round(x, 4) for x in interval] if interval else None,
                "zero_event_report": report}

    def mcnemar(metric):
        b = c = 0
        for q in both_ids:
            base, proto = _participant_cell(tables, q, "baseline", metric), _participant_cell(tables, q, "prototype", metric)
            if base[metric + ":den"] == 0 or proto[metric + ":den"] == 0:
                continue
            base_event, proto_event = base[metric + ":num"] > 0, proto[metric + ":num"] > 0
            b += base_event and not proto_event
            c += proto_event and not base_event
        return {"baseline_only_event": b, "prototype_only_event": c, "p_value_exact_two_sided": round(mcnemar_exact(b, c), 4),
                "note": "exploratory; never an acceptance verdict"}

    def trial_zero_report(condition, metric):
        eligible, with_event = eligible_counts(condition, metric)
        return zero_event_report(sum(c[metric + ":num"] for c in eligible), sum(c[metric + ":den"] for c in eligible),
                                 with_event, len(eligible))

    def stage2_inputs(condition, metric):
        eligible, _ = eligible_counts(condition, metric)
        clusters = [(c[metric + ":num"], c[metric + ":den"]) for c in eligible]
        trials = sum(m for _, m in clusters)
        rho = icc_anova(clusters)
        mean_trials = trials / len(clusters) if clusters else None
        return {"p_trial": _rounded(rate(total(tables, ids, (condition, ("all",))), metric)), "participants": len(clusters),
                "mean_trials_per_participant": _rounded(mean_trials), "rho_hat_anova": _rounded(rho),
                "deff_hat": _rounded(None if rho is None or mean_trials is None else 1 + (mean_trials - 1) * max(rho, 0.0))}

    def period1(condition, metric):
        return _rounded(rate(total(tables, ids, (condition, ("period", 1))), metric))

    return {
        "design": {"unit_of_analysis": "participant", "trials": len(records), "participants": len(ids),
                   "participants_with_both_conditions": len(both_ids), "paired": True, "crossed": "AB/BA",
                   "sequences": dict(Counter(strata.values())), "resampling_stratified_by_sequence": True,
                   "resamples": resamples if len(ids) >= 2 else 0, "resamples_default": DEFAULT_RESAMPLES,
                   "seed": str(seed), "trials_per_condition_and_period": dict(Counter(f"{t['condition']}@period{t['period']}" for t in records)),
                   "independence_of_trials": "NOT_ASSUMED", "study_stage": "STAGE_1_FORMATIVE_ESTIMATION",
                   "bootstrap_replicates": resamples if len(ids) >= 2 else 0, "bootstrap_seed": str(seed),
                   "small_cluster_warning": len(ids) < SMALL_CLUSTER_REFERENCE,
                   "very_small_cluster_descriptive_only": len(ids) < VERY_SMALL_CLUSTER,
                   "bca_policy": {"conditions": "C1 participants>=20; C2 each AB/BA stratum >= min_per_sequence (" + BCA_C2_THRESHOLD_STATUS + "); C3 variation and events; C4 valid bias/acceleration/adjusted quantiles", "min_per_sequence": BCA_MIN_PER_SEQUENCE, "min_participants": BCA_MIN_PARTICIPANTS, "min_with_event": BCA_MIN_WITH_EVENT,
                                  "min_without_event": BCA_MIN_WITHOUT_EVENT, "otherwise": BCA_FALLBACK},
                   "small_cluster_note": "fewer participants than the literature reference for stable cluster-bootstrap coverage (30); read intervals with caution and with the model-based estimates once available"},
        "trial_level_metrics": {
            "note": "Rates per trial pooled over trials; participants are the resampling unit.",
            "by_condition": {c: {m: cell(m, c, ("all",)) for m in METRICS} for c in CONDITIONS},
            "by_condition_and_modality": {c: {mod: {m: cell(m, c, ("modality", mod)) for m in METRICS} for mod in modalities} for c in CONDITIONS},
            "by_condition_and_scenario": {c: {sc: {m: cell(m, c, ("scenario", sc)) for m in METRICS} for sc in scenarios} for c in CONDITIONS},
            "by_condition_and_platform": {c: {pl: {m: cell(m, c, ("platform", pl)) for m in METRICS} for pl in platforms} for c in CONDITIONS},
            "paired_difference_prototype_minus_baseline": {m: paired(rates(m), ("all",), m) for m in METRICS},
            "paired_difference_by_modality": {mod: {m: paired(rates(m), ("modality", mod), m) for m in METRICS} for mod in modalities},
            "additional_time_seconds_prototype_minus_baseline": paired(mean_seconds, ("all",)),
        },
        "participant_level_metrics": {
            "note": "Share of participants with at least one event among those with at least one eligible trial.",
            "by_condition": {c: {m: participant_cell(m, c) for m in PARTICIPANT_METRICS} for c in CONDITIONS},
            "paired_difference_prototype_minus_baseline": {m: participant_paired(m) for m in PARTICIPANT_METRICS},
            "exact_over_participants": {c: {m: participant_exact(c, m) for m in PARTICIPANT_METRICS} for c in CONDITIONS},
            "mcnemar_exact": {m: mcnemar(m) for m in PARTICIPANT_METRICS},
        },
        "zero_event_reports": {c: {m: trial_zero_report(c, m) for m in PARTICIPANT_METRICS} for c in CONDITIONS},
        "crossover_and_device_models": {
            "status": "NOT_IMPLEMENTED_STDLIB_ONLY",
            "primary_model_prespecified": "logistic GLMM: intervention + period + sequence + device + participant random intercept (preferred; needs a statistics package)",
            "marginal_alternative_prespecified": "GEE exchangeable with small-sample robust variance (Mancl-DeRouen / Kauermann-Carroll)",
            "carryover_pretest": "PROHIBITED_NEVER_PERFORMED",
            "period1_sensitivity_descriptive": {"note": "pre-planned sensitivity analysis; no power control; between-participant; never a conditional switch",
                                                "by_condition": {c: {m: period1(c, m) for m in PARTICIPANT_METRICS} for c in CONDITIONS}},
        },
        "stage2_planning_inputs": {c: {m: stage2_inputs(c, m) for m in PARTICIPANT_METRICS} for c in CONDITIONS},
        "acceptance_decision": "PENDING_PHYSICIAN_OWNER_REVIEW",
        "period_and_learning": {
            "note": "Period effect = period 2 minus period 1 and learning = late minus early trials, both pooled over conditions; "
                    "stratified resampling keeps the AB/BA balance so they are not read as condition effects.",
            "period_effect_period2_minus_period1": {m: contrast(m, ("period", 2), ("period", 1)) for m in PARTICIPANT_METRICS},
            "learning_late_minus_early": {m: contrast(m, ("order", "late"), ("order", "early")) for m in PARTICIPANT_METRICS},
            "early_late_split": {"median_order_in_period": median_order, "early": "order_in_period <= median", "late": "order_in_period > median"},
        },
        "by_participant": {p: {c: {"trials": tables[p].get((c, ("all",)), Counter())["trials"],
                                   **{m: _rounded(rate(tables[p].get((c, ("all",)), Counter()), m)) for m in METRICS}}
                               for c in CONDITIONS} for p in ids},
        "descriptive_exploration_only": {"note": DESCRIPTIVE_NOTE,
                                         "by_condition": {c: {m: _descriptive([t for t in records if t["condition"] == c], m) for m in METRICS}
                                                          for c in CONDITIONS}},
        "limitations": list(LIMITATIONS),
        "acceptance_margin": "NOT_SET_MEDICAL_DECISION",
        "sample_size": "NOT_SET_STUDY_DESIGN_DECISION",
        "study_status": "NOT_EXECUTED_TOOLING_ONLY",
    }


TOOL_VERSION = "hf-tools-0.5"
SCENARIO_FIELDS = {"scenario_id", "intended_modality", "synthetic", "case_code", "platforms"}
SCENARIO_OPTIONAL = {"bank_set", "stimulus_sha256"}
BANK_SETS = ("set1", "set2")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MANIFEST_FIELDS = {"manifest_version", "scenarios"}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def validate_manifest(manifest):
    """Versioned list of SYNTHETIC scenarios: closed fields, opaque case codes, no free text and no image content."""
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS:
        raise ValueError(f"manifest fields must be exactly {sorted(MANIFEST_FIELDS)}")
    if not isinstance(manifest["manifest_version"], str) or not CODE.match(manifest["manifest_version"]):
        raise ValueError("manifest_version must be a version code (letters, digits, - and _ only)")
    scenarios = manifest["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a non-empty list")
    seen, case_codes, hashes = set(), {}, set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or not SCENARIO_FIELDS <= set(scenario) <= SCENARIO_FIELDS | SCENARIO_OPTIONAL:
            raise ValueError(f"scenario fields must be {sorted(SCENARIO_FIELDS)} plus optionally {sorted(SCENARIO_OPTIONAL)}")
        for field in ("scenario_id", "case_code"):
            if not isinstance(scenario[field], str) or not CODE.match(scenario[field]):
                raise ValueError(f"{field} must be an opaque code (letters, digits, - and _ only)")
        if scenario["intended_modality"] not in MODALITIES:
            raise ValueError("unknown intended modality")
        if scenario["synthetic"] is not True:
            raise ValueError("every scenario must be synthetic (no patient data)")
        platforms = scenario["platforms"]
        if not isinstance(platforms, list) or not platforms or len(set(platforms)) != len(platforms) or any(x not in PLATFORMS for x in platforms):
            raise ValueError("platforms must be a non-empty list of distinct web/mobile values")
        if scenario["scenario_id"] in seen:
            raise ValueError(f"scenario {scenario['scenario_id']} is listed twice")
        seen.add(scenario["scenario_id"])
        bank = scenario.get("bank_set")
        if "bank_set" in scenario and bank not in BANK_SETS:
            raise ValueError("bank_set must be set1 or set2")
        if scenario["case_code"] in case_codes and case_codes[scenario["case_code"]] != bank:
            raise ValueError(f"case_code {scenario['case_code']} appears in both banks (the banks must be disjoint)")
        case_codes[scenario["case_code"]] = bank
        if "stimulus_sha256" in scenario:
            digest_value = scenario["stimulus_sha256"]
            if not isinstance(digest_value, str) or not SHA256.match(digest_value):
                raise ValueError("stimulus_sha256 must be 64 lowercase hexadecimal characters")
            if digest_value in hashes:
                raise ValueError("two scenarios share the same stimulus_sha256 (scenario identity must be unique)")
            hashes.add(digest_value)
    frozen = all("stimulus_sha256" in sc for sc in scenarios)
    return {"valid": True, "manifest_version": manifest["manifest_version"], "scenarios": len(scenarios), "sha256": digest(manifest),
            "stimuli_frozen": frozen, "banks": sorted({sc.get("bank_set") for sc in scenarios if "bank_set" in sc})}


def assign_sequences(participants, seed="r15"):
    """Balanced AB/BA allocation of pseudonymous participant codes (a deterministic seeded shuffle, then alternation)."""
    if not isinstance(participants, list) or not participants:
        raise ValueError("participants must be a non-empty list of pseudonymous codes")
    if len(set(participants)) != len(participants):
        raise ValueError("participant codes must be unique")
    for code in participants:
        if not isinstance(code, str) or not CODE.match(code):
            raise ValueError("participant must be a pseudonymous code (letters, digits, - and _ only)")
    order = sorted(participants)
    random.Random(f"{seed}:assign:{len(order)}").shuffle(order)
    allocation = {}
    for index, code in enumerate(order):
        sequence = "AB" if index % 2 == 0 else "BA"
        first, second = ("baseline", "prototype") if sequence == "AB" else ("prototype", "baseline")
        allocation[code] = {"sequence": sequence, "period1": first, "period2": second}
    counts = Counter(v["sequence"] for v in allocation.values())
    return {"allocation": {k: allocation[k] for k in sorted(allocation)}, "counts": dict(counts), "seed": str(seed),
            "note": "Allocation only; no participant has been recruited and no study has been run."}


def check_records_against_manifest(records, manifest):
    validate_manifest(manifest)
    known = {s["scenario_id"]: s for s in manifest["scenarios"]}
    for record in records:
        scenario = known.get(record["scenario_id"])
        if scenario is None:
            raise ValueError(f"scenario {record['scenario_id']} is not in the manifest")
        if record["intended_modality"] != scenario["intended_modality"]:
            raise ValueError(f"scenario {record['scenario_id']} has another intended modality in the manifest")
        if record["platform"] not in scenario["platforms"]:
            raise ValueError(f"scenario {record['scenario_id']} is not defined for platform {record['platform']}")


def export_package(payload, resamples=DEFAULT_RESAMPLES, seed="r15", git_commit_sha=None):
    """Reproducible export: summary + hashes of the records and of the versioned scenario manifest."""
    if not isinstance(payload, dict) or set(payload) != {"manifest", "records"}:
        raise ValueError("export input must contain exactly manifest and records")
    validate_records(payload["records"])
    check_records_against_manifest(payload["records"], payload["manifest"])
    if git_commit_sha is not None and not re.fullmatch(r"[0-9a-f]{7,40}", str(git_commit_sha)):
        raise ValueError("git_commit_sha must be a 7-40 character lowercase hexadecimal commit id")
    summary = summarize(payload["records"], resamples, seed)
    return {"study_stage": "STAGE_1_FORMATIVE_ESTIMATION", "git_commit_sha": git_commit_sha,
            "stimuli_manifest_sha256": digest(payload["manifest"]), "dataset_sha256": digest(payload["records"]),
            "bootstrap_replicates": resamples, "bootstrap_seed": str(seed), "tool_version": TOOL_VERSION, "manifest_version": payload["manifest"]["manifest_version"],
            "manifest_sha256": digest(payload["manifest"]), "records_sha256": digest(payload["records"]),
            "summary_sha256": digest(summary), "resamples": resamples, "seed": str(seed), "summary": summary,
            "study_status": "NOT_EXECUTED_TOOLING_ONLY"}


COMMANDS = ("validate", "summarize", "manifest", "assign", "export")


def run(argv, raw):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=COMMANDS,
                        help="stdin: records (validate, summarize), manifest, {participants} (assign) or {manifest, records} (export)")
    parser.add_argument("--resamples", type=int, default=DEFAULT_RESAMPLES)
    parser.add_argument("--seed", default="r15")
    parser.add_argument("--git-commit-sha", default=None, help="commit id recorded in the export (export only)")
    args = parser.parse_args(argv)
    payload = json.loads(raw.decode("utf-8"))
    if args.command == "manifest":
        return validate_manifest(payload)
    if args.command == "assign":
        if not isinstance(payload, dict) or "participants" not in payload:
            raise ValueError("assign input must be an object with participants")
        return assign_sequences(payload["participants"], args.seed)
    if args.command == "export":
        return export_package(payload, args.resamples, args.seed, args.git_commit_sha)
    if args.command == "validate":
        return {"valid": True, "records": validate_records(payload)}
    return summarize(payload, args.resamples, args.seed)


def main(argv=None):
    result = run(sys.argv[1:] if argv is None else argv, sys.stdin.buffer.read())
    sys.stdout.write(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
