#!/usr/bin/env python3
"""End-to-end review-only evidence pipeline."""
from __future__ import annotations
from evidence_clinical_diff import structured_diff
from evidence_change_classifier import classify,map_modules
from evidence_impact_report import build_impact

def evaluate_change(source,old_text,new_text,module_catalog):
 diff=structured_diff(old_text,new_text)
 triage=classify(new_text,source.get("domains",[]))
 domains=triage["domains"]
 modules=map_modules(domains,module_catalog)
 impact=build_impact(source,diff,modules)
 return {"diff":diff,"triage":triage,"impact":impact,
         "invariants":{"production_mutation":False,"auto_apply":False,
                       "human_review_required":True}}
