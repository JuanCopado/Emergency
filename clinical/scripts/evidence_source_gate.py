#!/usr/bin/env python3
"""Fail-closed trust gate for evidence surveillance sources."""
from __future__ import annotations
from urllib.parse import urlparse

APPROVED_TYPES={"government-health-authority","medicines-regulator","international-public-health-body","recognized-scientific-society","formal-guideline-body"}
PENDING={"specific-safety-endpoint-pending","official-authority-confirmed-specific-current-index-pending","specific-guideline-endpoint-pending"}

def assess_source(source:dict)->dict:
 url=source.get("url",""); host=(urlparse(url).hostname or "").lower()
 reasons=[]
 trusted=True
 if not url.startswith("https://"): trusted=False;reasons.append("https_required")
 if source.get("authority_type") not in APPROVED_TYPES: trusted=False;reasons.append("authority_type_not_approved")
 status=source.get("validation_status")
 proposal_eligible=trusted and status not in PENDING
 if status in PENDING: reasons.append("endpoint_validation_pending")
 return {"trusted_for_surveillance":trusted,"eligible_for_clinical_change_proposal":proposal_eligible,
         "review_signal_allowed":trusted,"host":host,"reasons":reasons,
         "requires_human_review":True,"auto_apply":False}
