#!/usr/bin/env python3
"""Urgent medication-safety report gate.

Consumes surveillance JSON and emits only review-required urgent candidates.
No clinical content is mutated.
"""
from __future__ import annotations
import argparse,json,pathlib
from cli_paths import input_file, output_file

def urgent_items(report:dict)->list[dict]:
    return [dict(x, requires_human_review=True, auto_apply=False) for x in report.get("review_queue",[]) if x.get("classification")=="urgent-safety"]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=input_file)
    parser.add_argument("--output", type=output_file, required=True)
    args = parser.parse_args()
    destination: pathlib.Path = output_file(args.output)
    report = json.loads(args.report.read_text())
    result = {"production_changes_applied": False,
              "urgent_review_queue": urgent_items(report)}
    destination.write_text(data=json.dumps(result, indent=2) + "\n", encoding="utf-8")

if __name__=="__main__":main()
