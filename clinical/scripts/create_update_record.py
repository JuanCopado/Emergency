#!/usr/bin/env python3
import json, argparse
from pathlib import Path

def make_update(module, current_source, current_rec, new_source, new_date, new_rec, impact, changes):
    return {
        "module": module,
        "detected_on": "",
        "current_source": current_source,
        "current_recommendation": current_rec,
        "new_source": new_source,
        "new_publication_date": new_date,
        "new_recommendation": new_rec,
        "evidence_level": "",
        "clinical_impact": impact,
        "changes_bedside_action": changes,
        "status": "pending_review",
        "review_notes": ""
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--module", required=True)
    p.add_argument("--current-source", required=True)
    p.add_argument("--current-rec", required=True)
    p.add_argument("--new-source", required=True)
    p.add_argument("--new-date", required=True)
    p.add_argument("--new-rec", required=True)
    p.add_argument("--impact", choices=["high","moderate","low"], required=True)
    p.add_argument("--changes-bedside-action", action="store_true")
    a = p.parse_args()
    print(json.dumps(make_update(
        a.module, a.current_source, a.current_rec, a.new_source,
        a.new_date, a.new_rec, a.impact, a.changes_bedside_action
    ), indent=2, ensure_ascii=False))
