#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT=Path(__file__).parents[1]
MODULES=ROOT/"MODULES.md"
RULES=ROOT/"qa"/"clinical-note-diagnostic-rules.json"
POLICY=ROOT/"qa"/"clinical-note-diagnostic-coverage-policy.json"

def _module_ids():
    ids=[]
    for line in MODULES.read_text(encoding="utf-8").splitlines():
        m=re.match(r"\| `([^`]+)`",line)
        if m: ids.append(m.group(1))
    return ids

def audit():
    modules=_module_ids()
    rules=json.loads(RULES.read_text(encoding="utf-8"))["syndromes"]
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    covered=set()
    for rule in rules:
        covered.add(rule["id"])
        covered.update(rule.get("differential",[]))
        covered.update(rule.get("must_not_miss",[]))
        for group in ("suggested_tests","treatment"):
            for item in rule.get(group,[]):
                covered.update(item.get("source_modules",[]))
    allowed=set()
    for vals in policy["allowed_non_diagnostic_modules"].values():
        allowed.update(vals)
    registered=set(modules)
    remaining=sorted(registered-covered)
    unexpected=sorted(set(remaining)-allowed)
    stale_allowed=sorted(allowed-registered)
    return {
      "module_count":len(modules),
      "diagnostic_rule_count":len(rules),
      "covered_or_routed_count":len(registered & covered),
      "allowed_non_diagnostic_count":len(registered & allowed),
      "remaining":remaining,
      "unexpected_uncovered":unexpected,
      "stale_allowed":stale_allowed,
      "status":"PASS" if not unexpected and not stale_allowed else "FAIL"
    }

if __name__=="__main__":
    result=audit()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
