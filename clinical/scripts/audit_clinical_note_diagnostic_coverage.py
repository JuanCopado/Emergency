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

def _record_source_modules(refs, registered, covered, invalid, rule_id, field):
    if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) and ref for ref in refs):
        invalid.append({"rule_id":rule_id, "field":field,
                        "reason":"source_modules must be a nonempty list of module IDs"})
        return
    for ref in refs:
        if ref in registered:
            covered.add(ref)
        else:
            invalid.append({"rule_id":rule_id, "field":field, "source_module":ref,
                            "reason":"source module is not registered"})

def audit():
    modules=_module_ids()
    rules=json.loads(RULES.read_text(encoding="utf-8"))["syndromes"]
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    registered=set(modules)
    covered=set()
    invalid_sources=[]
    for rule in rules:
        _record_source_modules(rule.get("source_modules", [rule["id"]]), registered,
                               covered, invalid_sources, rule["id"], "source_modules")
        # These are syndrome/routing identifiers, not source_modules declarations.
        covered.update(rule.get("differential",[]))
        covered.update(rule.get("must_not_miss",[]))
        for group in ("suggested_tests","treatment"):
            for index,item in enumerate(rule.get(group,[])):
                _record_source_modules(item.get("source_modules"), registered, covered,
                                       invalid_sources, rule["id"], f"{group}[{index}].source_modules")
    allowed=set()
    for vals in policy["allowed_non_diagnostic_modules"].values():
        allowed.update(vals)
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
      "invalid_source_modules":invalid_sources,
      "status":"PASS" if not unexpected and not stale_allowed and not invalid_sources else "FAIL"
    }

if __name__=="__main__":
    result=audit()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    raise SystemExit(0 if result["status"]=="PASS" else 1)
