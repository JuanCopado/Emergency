#!/usr/bin/env python3
"""Create a prediction-entry template from one blinded shard."""

import argparse
import json
from pathlib import Path

ALLOWED = ["positive", "negative", "abstain", "nondiagnostic"]

from cli_paths import input_file, output_file

def build(shard):
    cases = shard.get("cases", [])
    if not cases:
        raise ValueError("shard contains no cases")
    return {
        "schema_version": "1.0",
        "target_condition": shard.get("target_condition"),
        "shard_index": shard.get("shard_index"),
        "shard_count": shard.get("shard_count"),
        "allowed_classes": ALLOWED,
        "instructions": (
            "For every case choose exactly one allowed class and set an ISO-8601 "
            "prediction_frozen_at timestamp. Do not access any sealed reference."
        ),
        "predictions": [
            {
                "id": case["id"],
                "class": None,
                "prediction_frozen_at": None
            }
            for case in cases
        ]
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("shard", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    # Validate every supplied path before business processing. The launcher grants the roots.
    try:
        args.shard = input_file(args.shard)
        args.output = output_file(args.output)
    except argparse.ArgumentTypeError as error:
        p.error(str(error))
    data = build(json.loads(args.shard.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
