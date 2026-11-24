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


# ---------------------------------------------------------------------------------------------------------------------------------
# R30 · NORMATIVE driver matrix S1a-S4b (R29_GEMINI_INFORME_MAESTRO_INTEGRADO, part IV, "MATRIZ-NORMATIVA-S1-S4-R29-CONGELABLE").
# Supersedes PUBLISHED (R27, 16/14) and CANDIDATE (same device pattern, no sets, no C/D). Laboratory only; no clinical content.
# ---------------------------------------------------------------------------------------------------------------------------------
import random

PAIR_MECHANISM = {**{p: "M3" for p in (1, 2, 3)}, **{p: "M1" for p in (4, 5, 6, 7)}, **{p: "M3" for p in range(8, 14)}, 14: "M2", 15: "M2"}
PAIR_SCENARIO = {1: "A", 2: "A", 3: "A", 4: "B", 5: "B", 6: "C", 7: "D", 8: "F", 9: "F", 10: "F", 11: "F", 12: "F", 13: "F", 14: "E1", 15: "E2"}
# Part IV s.10: pairs per sub-block. The C/D pair swaps between cycle a (C first) and cycle b (D first).
SUB1_FIXED = (4, 14, 1, 3, 8, 11, 13)
SUB2_FIXED = (5, 15, 2, 9, 10, 12)
WASHOUT_MINUTES = 10
BLOCK_SIZE = 4

# code -> (period-1 arm, set, device order, period-2 arm, set, device order); device order is (sub-block 1 device, sub-block 2 device)
_P1_M8, _P1_W8 = ("mobile", "web"), ("web", "mobile")
NORMATIVE_R29 = {
    "S1a": (("A", "SET_1", _P1_M8), ("B", "SET_2", _P1_W8), ("C", "D")),
    "S2a": (("A", "SET_2", _P1_W8), ("B", "SET_1", _P1_M8), ("C", "D")),
    "S3a": (("B", "SET_2", _P1_M8), ("A", "SET_1", _P1_W8), ("C", "D")),
    "S4a": (("B", "SET_1", _P1_W8), ("A", "SET_2", _P1_M8), ("C", "D")),
    "S1b": (("A", "SET_2", _P1_M8), ("B", "SET_1", _P1_W8), ("D", "C")),
    "S2b": (("A", "SET_1", _P1_W8), ("B", "SET_2", _P1_M8), ("D", "C")),
    "S3b": (("B", "SET_1", _P1_M8), ("A", "SET_2", _P1_W8), ("D", "C")),
    "S4b": (("B", "SET_2", _P1_W8), ("A", "SET_1", _P1_M8), ("D", "C")),
}


def _sub_pairs(subblock, cd_first):
    """Pairs of one sub-block: the fixed ones plus the C or D pair (6 = C, 7 = D) the cycle assigns to it."""
    letter = cd_first if subblock == 1 else ("D" if cd_first == "C" else "C")
    return (SUB1_FIXED if subblock == 1 else SUB2_FIXED) + ((6,) if letter == "C" else (7,))


def expand_normative(code, seed="HF1-R30", matrix=None):
    """Ordered trials of one participant for a normative code. Order inside a sub-block is pseudo-random with a registered seed and
    never starts a period with two consecutive M1 trials; the device changes exactly once per period (between sub-blocks)."""
    spec = (NORMATIVE_R29 if matrix is None else matrix)[code]
    p1, p2, (cd1, _cd2) = spec[0], spec[1], spec[2]
    trials = []
    for period, (arm, set_id, devices) in enumerate((p1, p2), 1):
        rng = random.Random(f"{seed}|{code}|{period}")
        for subblock, device in enumerate(devices, 1):
            pairs = list(_sub_pairs(subblock, cd1))
            while True:
                rng.shuffle(pairs)
                if not (subblock == 1 and PAIR_MECHANISM[pairs[0]] == "M1" and PAIR_MECHANISM[pairs[1]] == "M1"):
                    break
            for pair in pairs:
                prefix = "S1" if set_id == "SET_1" else "S2"
                trials.append({"code": code, "period": period, "subblock": subblock, "arm": arm, "set_id": set_id, "device": device,
                               "pair": pair, "stimulus_id": f"{prefix}-{pair:02d}", "mechanism": PAIR_MECHANISM[pair],
                               "scenario": PAIR_SCENARIO[pair]})
    return trials


def audit_normative(matrix=None, manifest=None):
    """Checks every R29 criterion that is decidable from the matrix (and the stimuli manifest when given). Never raises."""
    matrix = NORMATIVE_R29 if matrix is None else matrix
    violations = []
    if sorted(matrix) != sorted(f"S{n}{c}" for n in (1, 2, 3, 4) for c in "ab"):
        violations.append("the matrix must hold exactly S1a..S4b")
        return {"ok": False, "violations": violations}
    cells = Counter()
    for code, spec in matrix.items():
        try:
            trials = expand_normative(code, matrix=matrix)
        except Exception as error:                                                       # a malformed row is a violation, not a crash
            violations.append(f"{code}: cannot be expanded ({error})")
            continue
        (a1, s1, _), (a2, s2, _), (c1, c2) = spec
        if {a1, a2} != {"A", "B"} or {s1, s2} != {"SET_1", "SET_2"}:
            violations.append(f"{code}: each participant needs one A and one B period and Set 1 and Set 2 once")
        if (c1, c2) not in (("C", "D"), ("D", "C")):
            violations.append(f"{code}: C/D assignment invalid")
        if len(trials) != 30 or Counter(t["device"] for t in trials) != {"mobile": 15, "web": 15}:
            violations.append(f"{code}: not 30 trials with 15 mobile + 15 web")
        for period in (1, 2):
            rows = [t for t in trials if t["period"] == period]
            if len(rows) != 15 or Counter(t["mechanism"] for t in rows) != {"M1": 4, "M2": 2, "M3": 9}:
                violations.append(f"{code} period {period}: needs 15 trials with M1=4, M2=2, M3=9")
            if sorted(t["pair"] for t in rows) != list(range(1, 16)):
                violations.append(f"{code} period {period}: every stimulus pair must appear exactly once")
            sizes = Counter(t["subblock"] for t in rows)
            if sizes != {1: 8, 2: 7} or len({t["device"] for t in rows if t["subblock"] == 1}) != 1 \
                    or {t["device"] for t in rows if t["subblock"] == 1} == {t["device"] for t in rows if t["subblock"] == 2}:
                violations.append(f"{code} period {period}: sub-blocks must be 8 + 7 with a single device change")
            for device in ("mobile", "web"):
                counts = Counter(t["mechanism"] for t in rows if t["device"] == device)
                if (counts["M1"], counts["M2"]) != (2, 1):
                    violations.append(f"{code} period {period} {device}: needs 2 M1 + 1 M2 per device")
            first = [t for t in rows if t["subblock"] == 1][:2]
            if all(t["mechanism"] == "M1" for t in first):
                violations.append(f"{code} period {period}: starts with two consecutive M1")
        for t in trials:
            cells[(t["code"][-1], t["arm"], t["period"], t["device"])] += 1
        if manifest is not None:
            index = {e["stimulus_id"]: e for e in manifest["stimuli"]}
            for t in trials:
                entry = index.get(t["stimulus_id"])
                if entry is None or entry["scenario_code"] != t["scenario"] or entry["mechanism_id"] != t["mechanism"] \
                        or entry["set_id"] != int(t["set_id"][-1]) or entry["pair_id"] != t["pair"]:
                    violations.append(f"{code}: {t['stimulus_id']} disagrees with the stimuli manifest")
                    break
    for cycle in "ab":
        if any(count != 15 for key, count in cells.items() if key[0] == cycle) or len([k for k in cells if k[0] == cycle]) != 8:
            violations.append(f"cycle {cycle}: every (arm, period, device) cell of a block of 4 must hold exactly 15 trials")
    if {matrix[f"S{n}a"][2] for n in (1, 2, 3, 4)} != {("C", "D")} or {matrix[f"S{n}b"][2] for n in (1, 2, 3, 4)} != {("D", "C")}:
        violations.append("C/D must alternate between cycle a and cycle b")
    for cycle in "ab":                                                                       # AB/BA 2:2 and Set 1 twice in each period per block
        firsts = [matrix[f"S{n}{cycle}"][0] for n in (1, 2, 3, 4)]
        if Counter(f[0] for f in firsts) != {"A": 2, "B": 2} or Counter(f[1] for f in firsts) != {"SET_1": 2, "SET_2": 2}:
            violations.append(f"cycle {cycle}: sequence and set must be balanced 2:2 in period 1")
    return {"ok": not violations, "violations": violations, "codes": len(matrix)}
