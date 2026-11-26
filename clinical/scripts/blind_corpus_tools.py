#!/usr/bin/env python3
"""R12 · tooling for the independent blind R5-2 corpus (DEC-CLIN-R8-06B). Standard library only.

This module never loads the shipped filter and never contains corpus text. It prepares what an
independent custodian needs: a manifest of counts and hash, adjudication packets without labels,
validation of adjudicator records and agreement statistics. Isolation by construction: it has NO
file-system access at all. Input arrives on standard input and output goes to standard output, so
the custodian alone decides where corpus, packets and keys live (outside the repository); a test
fails if this module ever opens, reads or writes a file. Nothing here authorises a new expression
or a change of the filter, and none of it measures clinical performance.
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict

LANGUAGES = ("es-ES", "pt-PT", "pt-BR", "en")
CLASSES = ("explicit_reassurance", "implicit_paraphrase", "negated_warning", "neutral_descriptive",
           "unicode_variant", "homoglyph", "contradiction")
# Proposed adjudication question: does the text tell the reader the lesion is harmless or needs no assessment?
VERDICTS = ("reassures", "does_not_reassure", "cannot_decide")
ITEM_FIELDS = {"id", "lang", "class", "text"}
FORBIDDEN_ITEM_FIELDS = {"label", "expected", "note", "filter_result", "intercepted"}


def parse_items(raw):
    """Validate a corpus given as bytes; returns (items, sha256 of the exact bytes)."""
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


def manifest(raw):
    """Counts and hash only; never text."""
    items, digest = parse_items(raw)
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


ROLES = ("author", "evaluator", "custodian", "adjudicator")


def check_roles(roles):
    """Independence of the blind corpus: nobody may hold two roles. `roles` maps role -> list of names.

    Returns the people per role; raises ValueError naming every person who appears in more than one role
    (authors wrote the corpus, evaluators ran the filter, custodians keep the key, adjudicators judge).
    """
    if not isinstance(roles, dict) or set(roles) - set(ROLES):
        raise ValueError(f"roles must be an object with keys from {list(ROLES)}")
    held = defaultdict(list)
    for role in ROLES:
        names = roles.get(role, [])
        if not isinstance(names, list) or any(not isinstance(n, str) or not n.strip() for n in names):
            raise ValueError(f"role {role}: names must be a list of non-empty strings")
        if len(set(names)) != len(names):
            raise ValueError(f"role {role}: duplicated name")
        for name in names:
            held[name].append(role)
    clashes = {name: rs for name, rs in held.items() if len(rs) > 1}
    if clashes:
        raise ValueError(f"role separation violated: {json.dumps(clashes, sort_keys=True)}")
    if len(roles.get("adjudicator", [])) < 3:
        raise ValueError("at least three adjudicators are needed (two primary plus one tiebreaker)")
    return {role: sorted(roles.get(role, [])) for role in ROLES}


def agreement(items, records, adjudicators):
    """Per-language agreement of the two primary adjudicators and the items that need the tiebreaker."""
    first, second = adjudicators
    if first == second:
        raise ValueError("the two primary adjudicators must be different people")
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
    if len({first, second, tiebreaker}) != 3:
        raise ValueError("the two primary adjudicators and the tiebreaker must be three different people")
    a, b = votes.get(first), votes.get(second)
    if a and a == b and a != "cannot_decide":
        return a
    t = votes.get(tiebreaker)
    return t if t and t != "cannot_decide" else "unresolved"


def run(argv, raw):
    """Execute one command over the bytes received on standard input; returns the JSON-able result."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("manifest", help="stdin: corpus -> counts and hash")
    p = sub.add_parser("packets", help="stdin: corpus -> {packet, key}")
    p.add_argument("--adjudicator", required=True)
    p.add_argument("--langs", nargs="+", required=True, choices=LANGUAGES)
    p.add_argument("--seed", required=True)
    p = sub.add_parser("agreement", help='stdin: {"corpus": {...}, "adjudications": [...], "roles": {...}?} -> agreement')
    p.add_argument("--primary", nargs=2, required=True)
    sub.add_parser("roles", help='stdin: {"author": [...], "evaluator": [...], "custodian": [...], "adjudicator": [...]} -> people per role')
    args = parser.parse_args(argv)
    if args.command == "roles":
        return check_roles(json.loads(raw.decode("utf-8")))
    if args.command == "manifest":
        return manifest(raw)
    if args.command == "packets":
        items, _ = parse_items(raw)
        packet, key = make_packet(items, args.adjudicator, set(args.langs), args.seed)
        return {"packet": packet, "key": key}
    bundle = json.loads(raw.decode("utf-8"))
    items, _ = parse_items(json.dumps(bundle["corpus"]).encode("utf-8"))
    validate_adjudication(bundle["adjudications"], items)
    if "roles" in bundle:
        people = check_roles(bundle["roles"])
        outsiders = {r["adjudicator"] for r in bundle["adjudications"]} | set(args.primary)
        if outsiders - set(people["adjudicator"]):
            raise ValueError(f"adjudications by people outside the adjudicator role: {sorted(outsiders - set(people['adjudicator']))}")
    return agreement(items, bundle["adjudications"], args.primary)


def main(argv=None):
    result = run(sys.argv[1:] if argv is None else argv, sys.stdin.buffer.read())
    sys.stdout.write(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
