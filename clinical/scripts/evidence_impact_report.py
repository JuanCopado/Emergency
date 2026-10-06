#!/usr/bin/env python3
"""Build non-production clinical impact proposals from surveillance findings."""
from __future__ import annotations
def build_impact(source, diff, candidate_modules):
 return {
  "source_id":source["id"],"source_organization":source["organization"],"source_url":source["url"],
  "priority":diff["priority"],"change_categories":sorted(diff["categories"]),
  "candidate_module_ids":sorted(set(candidate_modules)),
  "clinical_change_authorized":False,"requires_clinician_review":True,
  "requires_pharmacist_review":bool({"dose_change","contraindication_change","safety_change","withdrawal_change"} & set(diff["categories"])),
  "qa_required":True,"status":"pending_review",
 }
