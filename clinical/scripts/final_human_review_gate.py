#!/usr/bin/env python3
"""Project-wide final human review queue for all yellow modules."""
import json
from pathlib import Path

ROOT=Path(__file__).parents[1]
EVIDENCE=ROOT/"references"/"evidence-registry.json"

def build_review_queue(root=ROOT):
    data=json.loads((Path(root)/"references"/"evidence-registry.json").read_text(encoding="utf-8"))
    modules=data["modules"]
    queue=[]
    for module_id,entry in sorted(modules.items()):
        if entry.get("status")=="yellow":
            queue.append({
                "module_id":module_id,
                "status":"NOT_REVIEWED",
                "priority":entry.get("priority","standard"),
                "required_reviews":["clinical"],
                "notes":[],
            })
            if any(token in module_id for token in ("medication","pharmac","infusion","toxic","anticoag","sedation","antibiotic")):
                queue[-1]["required_reviews"].append("pharmacy")
            if any(token in module_id for token in ("image","clinical-note","documentation")):
                queue[-1]["required_reviews"].append("privacy_information_governance")
    return {
        "policy":"all evidence-registry modules with status yellow remain pending final human review",
        "promotion_allowed_only_after":["required human reviews complete","critical findings resolved","Clinical QA PASS after corrections"],
        "yellow_count":len(queue),
        "queue":queue,
    }

def can_promote(review_item):
    return review_item.get("status") in {"PASS","PASS_WITH_NONCRITICAL_NOTE"} and review_item.get("qa_after_review")=="PASS"

if __name__=="__main__":
    print(json.dumps(build_review_queue(),indent=2,ensure_ascii=False))
