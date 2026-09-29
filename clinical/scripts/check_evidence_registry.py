#!/usr/bin/env python3
import json, argparse
from datetime import date, datetime
from pathlib import Path

DEFAULT_WINDOWS = {"high": 30, "standard": 90, "low": 180}

def days_since(iso_date):
    d = datetime.strptime(iso_date, "%Y-%m-%d").date()
    return (date.today() - d).days

def check_registry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    results = []
    for module, info in data["modules"].items():
        priority = info.get("priority", "standard")
        window = data.get("review_policy", {}).get(
            f"{'high_risk' if priority=='high' else 'standard' if priority=='standard' else 'low_change'}_days",
            DEFAULT_WINDOWS.get(priority, 90)
        )
        age = days_since(info["last_checked"])
        stored_status = info.get("status", "yellow")
        due = age > window or stored_status in ("yellow", "red")
        results.append({
            "module": module,
            "priority": priority,
            "stored_status": stored_status,
            "days_since_check": age,
            "review_window_days": window,
            "review_due": due
        })
    return results

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--registry", default="references/evidence-registry.json")
    args = p.parse_args()
    for item in check_registry(args.registry):
        print(json.dumps(item, ensure_ascii=False))
