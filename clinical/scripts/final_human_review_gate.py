#!/usr/bin/env python3
"""Project-wide final human review queue for all yellow modules."""
import json
from pathlib import Path

ROOT=Path(__file__).parents[1]
POLICY = json.loads((ROOT / "qa" / "final-human-review-policy.json").read_text(encoding="utf-8"))

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
                "clinical_decision_owner": POLICY["clinical_decision_owner"],
                "notes":[],
            })
            if any(token in module_id for token in ("image","clinical-note","documentation")):
                queue[-1]["required_reviews"].append("privacy_information_governance")
    return {
        "policy":"all evidence-registry modules with status yellow remain pending final human review",
        "promotion_allowed_only_after":POLICY["required_before_green"],
        "yellow_count":len(queue),
        "queue":queue,
    }

def can_promote(review_item):
    """Eligibility for this reviewed module. This function never changes its status."""
    decision = review_item.get("owner_decision")
    if not isinstance(decision, dict) or decision.get("approved") is not True:
        return False
    module_id = review_item.get("module_id")
    if not module_id or decision.get("module_id") != module_id:
        return False
    dossier = review_item.get("evidence_ref")
    return bool(
        dossier and decision.get("evidence_ref") == dossier
        and decision.get("reviewer") == POLICY["clinical_decision_owner"]
        and decision.get("date")
        and review_item.get("status") in {"PASS", "PASS_WITH_NONCRITICAL_NOTE"}
        and review_item.get("qa_after_review") == "PASS"
    )

if __name__=="__main__":
    print(json.dumps(build_review_queue(),indent=2,ensure_ascii=False))
