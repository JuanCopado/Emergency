#!/usr/bin/env python3
"""Structured, conservative clinical diff for evidence surveillance."""
from __future__ import annotations
import re
CATS={
"dose_change":(" mg"," mcg"," µg"," ml","mg/kg","mcg/kg","ml/h","dose","dosage","dose máxima","maximum dose"),
"contraindication_change":("contraindicat","contraindica","do not use","não utilizar"),
"indication_change":("indication","indicated","indicação","indicado"),
"safety_change":("warning","safety","alert","risk","segurança","alerta","risco"),
"recommendation_change":("recommend","guideline","recomend","diretriz","orientação"),
"algorithm_change":("algorithm","pathway","flowchart","algorit","via clínica"),
"withdrawal_change":("withdraw","removed","no longer recommended","retirad","suspens","deixou de ser recomendado"),
}
CRITICAL={"contraindication_change","safety_change","withdrawal_change"}
HIGH={"dose_change","indication_change","algorithm_change"}
def lines(text): return {re.sub(r"\s+"," ",x).strip() for x in (text or "").splitlines() if x.strip()}
def structured_diff(old,new):
 added=lines(new)-lines(old); removed=lines(old)-lines(new); changed=added|removed
 categories={}
 for cat,terms in CATS.items():
  hits=sorted(x for x in changed if any(t in x.lower() for t in terms))
  if hits: categories[cat]=hits[:20]
 if set(categories)&CRITICAL: priority="critical"
 elif set(categories)&HIGH: priority="high"
 elif categories: priority="moderate"
 else: priority="low"
 return {"categories":categories,"priority":priority,"added_count":len(added),"removed_count":len(removed),"requires_human_review":bool(changed),"auto_apply":False}
