"""R28 · Device counterbalancing S1-S4 for the lab driver: the matrix as PUBLISHED in R27_GEMINI_INFORME_INTEGRADO_FINAL (part I, s.3)
and a CANDIDATE correction, both checked by the same invariants. Laboratory only; no clinical content.

Invariants (protocol R27): 30 trials per participant = 15 mobile + 15 desktop; 15 trials per period; each period is split into two
contiguous sub-blocks of 8 and 7 trials separated by one device change; the 8-block holds 2 M1 (B/C), 1 M2 (E1), 5 M3 and the 7-block
2 M1 (B/D), 1 M2 (E2), 4 M3; 2 M1 + 1 M2 per device per arm; AB and BA both present; device is not aliased with arm or period.

STATUS: PUBLISHED_MATRIX_FAILS_15_15; the candidate below is NOT validated by Gemini and must not be used for data collection until it is."""
from collections import Counter

SUBBLOCK_CONTENT = {8: {"M1": 2, "M2": 1, "M3": 5}, 7: {"M1": 2, "M2": 1, "M3": 4}}

# sequence -> ((arm, ((device, size), (device, size))), (arm, (...)))
PUBLISHED = {
    "S1": (("A", (("mobile", 8), ("web", 7))), ("B", (("web", 7), ("mobile", 8)))),
    "S2": (("A", (("web", 8), ("mobile", 7))), ("B", (("mobile", 7), ("web", 8)))),
    "S3": (("B", (("mobile", 8), ("web", 7))), ("A", (("web", 7), ("mobile", 8)))),
    "S4": (("B", (("web", 8), ("mobile", 7))), ("A", (("mobile", 7), ("web", 8)))),
}
# CANDIDATE: period 2 swaps the sub-block sizes so that every participant gets 8 + 7 on each device.
CANDIDATE = {
    "S1": (("A", (("mobile", 8), ("web", 7))), ("B", (("web", 8), ("mobile", 7)))),
    "S2": (("A", (("web", 8), ("mobile", 7))), ("B", (("mobile", 8), ("web", 7)))),
    "S3": (("B", (("mobile", 8), ("web", 7))), ("A", (("web", 8), ("mobile", 7)))),
    "S4": (("B", (("web", 8), ("mobile", 7))), ("A", (("mobile", 8), ("web", 7)))),
}


def audit(matrix):
    """Returns {'ok': bool, 'violations': [...], 'per_sequence': {...}, 'pooled_arm_device': {...}} without raising."""
    violations, per_sequence, pooled = [], {}, Counter()
    for name, periods in matrix.items():
        devices = Counter()
        if [arm for arm, _ in periods] not in (["A", "B"], ["B", "A"]):
            violations.append(f"{name}: arms are not one A and one B")
        for index, (arm, blocks) in enumerate(periods, 1):
            sizes = sorted(size for _, size in blocks)
            if sizes != [7, 8]:
                violations.append(f"{name} period {index}: sub-block sizes {sizes} != [7, 8]")
            if len(blocks) != 2 or blocks[0][0] == blocks[1][0]:
                violations.append(f"{name} period {index}: needs exactly one device change")
            if sum(size for _, size in blocks) != 15:
                violations.append(f"{name} period {index}: not 15 trials")
            for device, size in blocks:
                devices[device] += size
                pooled[(arm, device)] += size
        per_sequence[name] = dict(devices)
        if devices["mobile"] != 15 or devices["web"] != 15:
            violations.append(f"{name}: device totals mobile={devices['mobile']} web={devices['web']} (required 15/15)")
    if {periods[0][0] for periods in matrix.values()} != {"A", "B"}:
        violations.append("AB and BA sequences must both be present")
    for arm in ("A", "B"):
        if pooled[(arm, "mobile")] != pooled[(arm, "web")]:
            violations.append(f"arm {arm}: pooled device totals are unequal across the four sequences")
    if pooled[("A", "mobile")] != pooled[("B", "mobile")]:
        violations.append("device is aliased with arm across the four sequences")
    return {"ok": not violations, "violations": violations, "per_sequence": per_sequence,
            "pooled_arm_device": {f"{arm}/{device}": n for (arm, device), n in sorted(pooled.items())}}


def expand_trials(periods):
    """Ordered (period, arm, device, mechanism) tuples for one sequence; M1/M2/M3 content follows the sub-block size."""
    out = []
    for period, (arm, blocks) in enumerate(periods, 1):
        for device, size in blocks:
            for mechanism, n in SUBBLOCK_CONTENT[size].items():
                out.extend((period, arm, device, mechanism) for _ in range(n))
    return out
