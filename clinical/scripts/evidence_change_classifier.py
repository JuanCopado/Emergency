#!/usr/bin/env python3
"""Deterministic triage for evidence-surveillance proposals.

It maps source metadata/text signals to candidate clinical modules. Output is
review support only and can never authorize a clinical change.
"""
from __future__ import annotations
import re

URGENT_TERMS=("recall","withdraw","suspend","contraindicat","serious risk","safety alert","retirada","suspensão","contraindica","alerta de segurança")
DOMAIN_RULES={
 "cardiology":("cardiac","cardiology","myocard","coronary","arrhythm","heart failure","cardíac","coronár","arritm"),
 "resuscitation":("resuscitation","cardiac arrest","cpr","ressuscitação","paragem"),
 "medication-safety":("medicine","drug","medication","pharmacovigil","medicamento","fármaco","farmacovigil"),
 "pediatrics":("pediatric","paediatric","child","children","pediatr","criança"),
 "sepsis":("sepsis","septic","sépsis","séptico"),
 "neurology":("stroke","neurolog","ictus","avc","neurol"),
}
def normalize(text:str)->str: return re.sub(r"\s+"," ",(text or "").lower()).strip()
def classify(text:str, configured_domains:list[str]|None=None)->dict:
    t=normalize(text); domains=set(configured_domains or [])
    for domain,terms in DOMAIN_RULES.items():
        if any(x in t for x in terms): domains.add(domain)
    urgent=any(x in t for x in URGENT_TERMS)
    return {"classification":"urgent-safety" if urgent else "potentially-practice-changing","domains":sorted(domains),"requires_human_review":True,"auto_apply":False}
def map_modules(domains:list[str], module_catalog:list[dict])->list[str]:
    wanted=set(domains); out=[]
    for m in module_catalog:
        tags=set(m.get("domains",[]))|set(m.get("tags",[]))
        if wanted & tags: out.append(m["id"])
    return sorted(set(out))
