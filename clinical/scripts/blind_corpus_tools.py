#!/usr/bin/env python3
"""R12 · tooling for the independent blind R5-2 corpus (DEC-CLIN-R8-06B). Standard library only.

This module never loads the shipped filter and never contains corpus text. It prepares what an
independent custodian needs: a manifest of counts and hash, adjudication packets without labels,
validation of adjudicator records and agreement statistics. The corpus, the packets and the keys
must live OUTSIDE the repository; every command refuses a path inside it. Nothing here authorises
a new expression or a change of the filter, and none of it measures clinical performance.
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = ("es-ES", "pt-PT", "pt-BR", "en")
CLASSES = ("explicit_reassurance", "implicit_paraphrase", "negated_warning", "neutral_descriptive",
           "unicode_variant", "homoglyph", "contradiction")
# Proposed adjudication question: does the text tell the reader the lesion is harmless or needs no assessment?
VERDICTS = ("reassures", "does_not_reassure", "cannot_decide")
ITEM_FIELDS = {"id", "lang", "class", "text"}
FORBIDDEN_ITEM_FIELDS = {"label", "expected", "note", "filter_result", "intercepted"}


def ensure_outside_repo(path, what):
    resolved = Path(path).resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise SystemExit(f"{what} must stay outside the repository (isolation): {resolved}")
    return resolved


def load_items(path):
    path = ensure_outside_repo(path, "corpus file")
    raw = path.read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    items = doc.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("corpus needs a non-empty 'items' list")
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("every item must be an object")
        extra = set(item) - ITEM_FIELDS
        if extra & FORBIDDEN_ITEM_FIELDS:
            raise ValueError(f"item {item.get('id')}: engineering labels are not allowed ({sorted(extra & FORBIDDEN_ITEM_FIELDS)})")
        if set(item) != ITEM_FIELDS:
            raise ValueError(f"item {item.get('id')}: fields must be exactly {sorted(ITEM_FIELDS)}")
        if item["lang"] not in LANGUAGES or item["class"] not in CLASSES:
            raise ValueError(f"item {item['id']}: unknown language or class")
        if not isinstance(item["text"], str) or not item["text"].strip():
            raise ValueError(f"item {item['id']}: empty text")
        if item["id"] in seen:
            raise ValueError(f"duplicate item id {item['id']}")
        seen.add(item["id"])
    return items, hashlib.sha256(raw).hexdigest()


def manifest(path):
    """Counts and hash only; never text."""
    items, digest = load_items(path)
    cells = Counter((item["lang"], item["class"]) for item in items)
    return {"sha256": digest, "items": len(items),
            "by_language": dict(Counter(item["lang"] for item in items)),
            "by_class": dict(Counter(item["class"] for item in items)),
            "cells": {f"{lang}|{cls}": cells.get((lang, cls), 0) for lang in LANGUAGES for cls in CLASSES},
            "empty_cells": [f"{lang}|{cls}" for lang in LANGUAGES for cls in CLASSES if not cells.get((lang, cls))]}


def make_packet(items, adjudicator, languages, seed):
    """A shuffled packet with opaque codes and no class or label, plus the key the custodian keeps."""
    rng = random.Random(f"{seed}:{adjudicator}")
    chosen = [item for item in items if item["lang"] in languages]
    rng.shuffle(chosen)
    key, packet = {}, []
    for index, item in enumerate(chosen, 1):
        code = f"{adjudicator}-{index:04d}-{rng.randrange(16**6):06x}"
        key[code] = item["id"]
        packet.append({"code": code, "lang": item["lang"], "text": item["text"]})
    return {"adjudicator": adjudicator, "verdicts_allowed": list(VERDICTS), "items": packet}, key


def validate_adjudication(records, items):
    ids = {item["id"] for item in items}
    seen = set()
    for record in records:
        if set(record) != {"adjudicator", "item", "verdict"}:
            raise ValueError(f"record fields must be adjudicator, item, verdict: {record}")
        if record["verdict"] not in VERDICTS:
            raise ValueError(f"unknown verdict {record['verdict']!r}")
        if record["item"] not in ids:
            raise ValueError(f"unknown item {record['item']!r}")
        pair = (record["adjudicator"], record["item"])
        if pair in seen:
            raise ValueError(f"adjudicator {pair[0]} judged {pair[1]} twice")
        seen.add(pair)
    return True


def cohen_kappa(first, second):
    """Cohen's kappa for two raters over the same items; None when chance agreement is total."""
    if not first or len(first) != len(second):
        raise ValueError("kappa needs two equal, non-empty rating lists")
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second)) / n
    ca, cb = Counter(first), Counter(second)
    chance = sum((ca[label] / n) * (cb[label] / n) for label in set(first) | set(second))
    return None if chance == 1 else (observed - chance) / (1 - chance)


def agreement(items, records, adjudicators):
    """Per-language agreement of the two primary adjudicators and the items that need the tiebreaker."""
    first, second = adjudicators
    by_lang = defaultdict(lambda: {"both": 0, "agree": 0, "a": [], "b": []})
    verdict = defaultdict(dict)
    for record in records:
        verdict[record["item"]][record["adjudicator"]] = record["verdict"]
    needs_tiebreak = []
    for item in items:
        votes = verdict.get(item["id"], {})
        if first in votes and second in votes:
            cell = by_lang[item["lang"]]
            cell["both"] += 1
            cell["a"].append(votes[first])
            cell["b"].append(votes[second])
            decided = votes[first] == votes[second] and votes[first] != "cannot_decide"
            cell["agree"] += votes[first] == votes[second]
            if not decided:
                needs_tiebreak.append(item["id"])
    return {"by_language": {lang: {"items_judged_by_both": c["both"],
                                   "percent_agreement": round(100 * c["agree"] / c["both"], 1),
                                   "cohen_kappa": cohen_kappa(c["a"], c["b"])}
                            for lang, c in by_lang.items() if c["both"]},
            "needs_tiebreak": sorted(needs_tiebreak)}


def final_label(votes, first, second, tiebreaker):
    """Two primary adjudicators agree -> that verdict; otherwise the tiebreaker; else unresolved."""
    a, b = votes.get(first), votes.get(second)
    if a and a == b and a != "cannot_decide":
        return a
    t = votes.get(tiebreaker)
    return t if t and t != "cannot_decide" else "unresolved"


def _write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("manifest")
    p.add_argument("corpus")
    p = sub.add_parser("packets")
    p.add_argument("corpus")
    p.add_argument("--adjudicator", required=True)
    p.add_argument("--langs", nargs="+", required=True, choices=LANGUAGES)
    p.add_argument("--seed", required=True)
    p.add_argument("--out", required=True, help="directory outside the repository")
    p = sub.add_parser("agreement")
    p.add_argument("corpus")
    p.add_argument("adjudications")
    p.add_argument("--primary", nargs=2, required=True)
    args = parser.parse_args(argv)
    items, _ = load_items(args.corpus)
    if args.command == "manifest":
        print(json.dumps(manifest(args.corpus), indent=1, ensure_ascii=False))
    elif args.command == "packets":
        out = ensure_outside_repo(args.out, "output directory")
        out.mkdir(parents=True, exist_ok=True)
        packet, key = make_packet(items, args.adjudicator, set(args.langs), args.seed)
        _write_json(out / f"packet-{args.adjudicator}.json", packet)
        _write_json(out / f"key-{args.adjudicator}.json", key)
        print(f"{len(packet['items'])} items; keep key-{args.adjudicator}.json with the custodian only")
    else:
        records = json.loads(ensure_outside_repo(args.adjudications, "adjudication file").read_text(encoding="utf-8"))
        validate_adjudication(records, items)
        print(json.dumps(agreement(items, records, args.primary), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
