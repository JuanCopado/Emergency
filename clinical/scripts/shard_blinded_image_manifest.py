#!/usr/bin/env python3
"""Shard a blinded image manifest into deterministic evaluation batches.

This operates only on the blinded manifest. It never reads sealed references.
Each case appears in exactly one shard, preserving patient grouping if requested.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

def shard(blinded, max_cases=50, keep_patient_groups=True):
    if max_cases <= 0:
        raise ValueError("max_cases must be >0")
    cases = blinded.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("blinded manifest must contain cases")

    seen = set()
    for case in cases:
        cid = case.get("id")
        if not cid or cid in seen:
            raise ValueError("case IDs must be present and unique")
        seen.add(cid)
        if keep_patient_groups and not case.get("patient_uid_hash"):
            raise ValueError(f"{cid}: patient_uid_hash required")

    ordered = sorted(cases, key=lambda x: x["id"])

    if not keep_patient_groups:
        groups = [[case] for case in ordered]
    else:
        by_patient = defaultdict(list)
        for case in ordered:
            by_patient[case["patient_uid_hash"]].append(case)
        groups = [
            sorted(group, key=lambda x: x["id"])
            for _, group in sorted(by_patient.items(), key=lambda kv: kv[0])
        ]

    shards = []
    current = []
    for group in groups:
        if len(group) > max_cases:
            raise ValueError(
                f"patient group {group[0]['patient_uid_hash']} has {len(group)} cases > max_cases"
            )
        if current and len(current) + len(group) > max_cases:
            shards.append(current)
            current = []
        current.extend(group)
    if current:
        shards.append(current)

    out = []
    total = len(cases)
    for i, shard_cases in enumerate(shards, start=1):
        out.append({
            "schema_version": "1.0",
            "dataset_id": blinded.get("source_id"),
            "source_version": blinded.get("source_version"),
            "target_condition": blinded.get("target_condition"),
            "target_question": blinded.get("target_question"),
            "shard_index": i,
            "shard_count": len(shards),
            "total_case_count": total,
            "case_count": len(shard_cases),
            "patient_grouping_preserved": bool(keep_patient_groups),
            "cases": [
                {
                    "id": c["id"],
                    "patient_uid_hash": c.get("patient_uid_hash"),
                    "study_uid_hash": c.get("study_uid_hash"),
                    "image_file": c.get("image_file"),
                }
                for c in shard_cases
            ],
        })
    return out

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("blinded_manifest", type=Path)
    p.add_argument("output_dir", type=Path)
    p.add_argument("--max-cases", type=int, default=50)
    p.add_argument("--allow-split-patient", action="store_true")
    args = p.parse_args()
    data = json.loads(args.blinded_manifest.read_text(encoding="utf-8"))
    shards = shard(data, args.max_cases, not args.allow_split_patient)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for item in shards:
        path = args.output_dir / f"shard-{item['shard_index']:04d}-of-{item['shard_count']:04d}.json"
        path.write_text(json.dumps(item, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"shard_count": len(shards), "case_count": len(data["cases"])}, ensure_ascii=False))
