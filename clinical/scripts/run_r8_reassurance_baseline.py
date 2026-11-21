#!/usr/bin/env python3
"""R8 · baseline of the current reassurance filter over the frozen synthetic corpus.

Read-only measurement: it applies the filter as shipped (`_fold` + `_REASSURANCE`) and reports
interception by language and class. Labels are engineering construction, not medical
adjudication, so the output is a regression baseline, not clinical sensitivity or specificity.
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import clinical_note_vision_adapter as adapter  # noqa: E402

CORPUS = ROOT / "qa" / "corpus" / "r8_reassurance_synthetic_corpus_v0.json"
PIN = ROOT / "qa" / "corpus" / "r8_reassurance_synthetic_corpus_v0.sha256"


def load(path=CORPUS, pin=PIN):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    expected = Path(pin).read_text(encoding="utf-8").split()[0]
    if digest != expected:
        raise SystemExit(f"corpus SHA-256 mismatch: {digest} != {expected}")
    return json.loads(raw.decode("utf-8")), digest


def intercepted(text):
    return bool(adapter._REASSURANCE.search(adapter._fold(text)))


def measure(corpus):
    cells = defaultdict(lambda: {"n": 0, "intercepted": 0})
    totals = {"reassure": [0, 0], "not_reassure": [0, 0], "ambiguous": 0}
    for case in corpus["cases"]:
        hit = intercepted(case["text"])
        key = f'{case["lang"]}|{case["class"]}|{case["label"]}'
        cells[key]["n"] += 1
        cells[key]["intercepted"] += hit
        if case["label"] == "reassure":
            totals["reassure"][0] += 1
            totals["reassure"][1] += hit
        elif case["label"] == "ambiguous":
            totals["ambiguous"] += 1
        else:
            totals["not_reassure"][0] += 1
            totals["not_reassure"][1] += hit
    by_lang = defaultdict(lambda: {"reassure": [0, 0], "not_reassure": [0, 0]})
    for case in corpus["cases"]:
        if case["label"] == "ambiguous":
            continue
        group = "reassure" if case["label"] == "reassure" else "not_reassure"
        by_lang[case["lang"]][group][0] += 1
        by_lang[case["lang"]][group][1] += intercepted(case["text"])
    return {
        "false_negatives": {"missed": totals["reassure"][0] - totals["reassure"][1], "of": totals["reassure"][0]},
        "false_positives": {"intercepted": totals["not_reassure"][1], "of": totals["not_reassure"][0]},
        "ambiguous_not_scored": totals["ambiguous"],
        "by_language": {lang: {"false_negatives": f'{v["reassure"][0] - v["reassure"][1]}/{v["reassure"][0]}',
                                "false_positives": f'{v["not_reassure"][1]}/{v["not_reassure"][0]}'}
                        for lang, v in sorted(by_lang.items())},
        "cells": dict(sorted(cells.items())),
    }


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    corpus, digest = load()
    result = {"corpus_sha256": digest, "scope": "regression baseline; not clinical performance", **measure(corpus)}
    text = json.dumps(result, ensure_ascii=False, indent=1)
    print(text)


if __name__ == "__main__":
    main()
