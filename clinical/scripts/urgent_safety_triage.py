#!/usr/bin/env python3
"""Urgent medication-safety report gate.

Consumes surveillance JSON and emits only review-required urgent candidates.
No clinical content is mutated.
"""
from __future__ import annotations
import argparse,json,pathlib
def urgent_items(report:dict)->list[dict]:
    return [dict(x, requires_human_review=True, auto_apply=False) for x in report.get("review_queue",[]) if x.get("classification")=="urgent-safety"]
def main():
    p=argparse.ArgumentParser();p.add_argument("report");p.add_argument("--output",required=True);a=p.parse_args()
    r=json.loads(pathlib.Path(a.report).read_text()); out={"production_changes_applied":False,"urgent_review_queue":urgent_items(r)}
    pathlib.Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__":main()
