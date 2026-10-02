#!/usr/bin/env python3
"""Merge completed blinded prediction shards before reference reveal."""

import argparse
import json
from pathlib import Path

ALLOWED = {"positive", "negative", "abstain", "nondiagnostic"}

def merge(prediction_files):
    predictions = {}
    shard_indices = set()
    expected_shard_count = None

    for path in prediction_files:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        shard_index = data.get("shard_index")
        shard_count = data.get("shard_count")
        if not isinstance(shard_index, int) or not isinstance(shard_count, int):
            raise ValueError(f"{path}: shard_index/shard_count required")
        if expected_shard_count is None:
            expected_shard_count = shard_count
        elif shard_count != expected_shard_count:
            raise ValueError("inconsistent shard_count")
        if shard_index in shard_indices:
            raise ValueError(f"duplicate shard_index {shard_index}")
        shard_indices.add(shard_index)

        for item in data.get("predictions", []):
            cid = item.get("id")
            if not cid or cid in predictions:
                raise ValueError(f"duplicate/missing prediction id: {cid}")
            if item.get("class") not in ALLOWED:
                raise ValueError(f"{cid}: invalid or incomplete class")
            if not item.get("prediction_frozen_at"):
                raise ValueError(f"{cid}: prediction_frozen_at required")
            predictions[cid] = {
                "id": cid,
                "class": item["class"],
                "prediction_frozen_at": item["prediction_frozen_at"],
            }

    expected = set(range(1, (expected_shard_count or 0) + 1))
    if shard_indices != expected:
        raise ValueError(
            f"incomplete shards; expected={sorted(expected)} got={sorted(shard_indices)}"
        )

    return {
        "schema_version": "1.0",
        "shard_count": expected_shard_count,
        "predictions": [predictions[cid] for cid in sorted(predictions)],
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("prediction_files", nargs="+", type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    result = merge(args.prediction_files)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"prediction_count": len(result["predictions"]), "shard_count": result["shard_count"]}))
