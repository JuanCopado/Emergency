#!/usr/bin/env python3
"""Transparent deterministic diagnostic-support engine for structured clinical notes.

This engine is not a calibrated diagnostic model. It applies explicit, inspectable
rules to privacy-cleared note content and routes recommendations to existing modules.
"""

import json
import re
from copy import deepcopy
from pathlib import Path

from clinical_note_support import diagnostic_support_contract

ROOT=Path(__file__).parents[1]
RULES_PATH=ROOT/"qa"/"clinical-note-diagnostic-rules.json"

def load_rules(path=RULES_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _norm(value):
    text=str(value or "").lower()
    text=(text.replace("á","a").replace("à","a").replace("ã","a").replace("â","a")
              .replace("é","e").replace("ê","e").replace("í","i")
              .replace("ó","o").replace("ô","o").replace("õ","o")
              .replace("ú","u").replace("ü","u").replace("ç","c")
              .replace("ñ","n"))
    return re.sub(r"\s+"," ",text).strip()

def _collect_text(note):
    parts=[]
    h=note.get("history",{})
    for key in ("chief_complaint","present_illness","social_history","baseline_status"):
        if h.get(key): parts.append(h[key])
    for key in ("past_medical_history","past_surgical_history","medication_discrepancies"):
        parts.extend(h.get(key) or [])
    for med in h.get("chronic_medications",[]):
        parts.append(" ".join(str(med.get(x) or "") for x in ("name","dose","schedule")))
    for event in note.get("timeline",[]):
        parts.append(str(event.get("event") or ""))
    ex=note.get("exam",{})
    for key in ("general","neurologic","respiratory","cardiovascular","abdominal","skin_wounds","extremities","other"):
        if ex.get(key): parts.append(ex[key])
    for section,reports in note.get("complementary_tests",{}).items():
        for r in reports:
            for key in ("official_report","ai_interpretation","findings","impression"):
                if r.get(key): parts.append(r[key])
    return _norm(" | ".join(str(x) for x in parts if x))

def _age_years(note):
    age=note.get("encounter",{}).get("age",{})
    if age.get("years") is not None:
        try:return float(age["years"])
        except Exception:return None
    if age.get("months") is not None:
        try:return float(age["months"])/12.0
        except Exception:return None
    return None

def _latest_vitals(note):
    vals=note.get("exam",{}).get("vitals",[]) or []
    return vals[-1] if vals else {}

def _structured_signals(note):
    v=_latest_vitals(note)
    age=_age_years(note)
    signals=[]
    try:
        spo2=float(v.get("spo2"))
        if spo2<90: signals.append(("hipoxemia",2,"SpO2 <90%"))
        elif spo2<94: signals.append(("mild_hypoxemia",1,"SpO2 <94%"))
    except Exception: pass
    try:
        temp=float(v.get("temperature_c"))
        if temp>=38.0: signals.append(("fever",1,"temperatura >=38°C"))
        if temp<35.0: signals.append(("hypothermia",1,"temperatura <35°C"))
    except Exception: pass
    bp=str(v.get("bp") or "")
    m=re.match(r"\s*(\d{2,3})\s*/",bp)
    if m and age is not None and age>=18:
        sbp=int(m.group(1))
        if sbp<90: signals.append(("hypotension",2,"PAS <90 mmHg"))
    gcs=str(v.get("gcs") or "").strip()
    m=re.match(r"(\d+)",gcs)
    if m:
        gv=int(m.group(1))
        if gv<13: signals.append(("altered_consciousness",2,"GCS <13"))
        elif gv<15: signals.append(("altered_consciousness",1,"GCS <15"))
    return signals

def _term_present(term,text):
    return _norm(term) in text

def _rule_score(rule,text,signals):
    score=0; evidence=[]
    signal_names={x[0] for x in signals}
    signal_labels={x[0]:x[2] for x in signals}
    for trig in rule.get("triggers",[]):
        t=trig.get("type")
        if t=="text_any":
            if any(_term_present(term,text) for term in trig.get("terms",[])):
                score += int(trig.get("weight",1))
                evidence.append(trig.get("label") or "hallazgo textual")
        elif t=="signal":
            if trig.get("signal") in signal_names:
                score += int(trig.get("weight",1))
                evidence.append(trig.get("label") or signal_labels.get(trig.get("signal")))
    # Cross-map structured signals to syndromes without pretending they are diagnostic.
    sid=rule["id"]
    if sid in {"sepsis-shock","tension-pneumothorax","abdominal-aortic-aneurysm"} and "hypotension" in signal_names:
        score+=2; evidence.append(signal_labels["hypotension"])
    if sid in {"pulmonary-embolism","acute-heart-failure","tension-pneumothorax"} and ("hipoxemia" in signal_names or "mild_hypoxemia" in signal_names):
        name="hipoxemia" if "hipoxemia" in signal_names else "mild_hypoxemia"
        score+=1; evidence.append(signal_labels[name])
    if sid=="sepsis-shock" and ("fever" in signal_names or "hypothermia" in signal_names):
        name="fever" if "fever" in signal_names else "hypothermia"
        score+=1; evidence.append(signal_labels[name])
    return score,list(dict.fromkeys(evidence))

def _confidence(score, thresholds):
    if score>=thresholds["high"]["minimum_score"]: return "high"
    if score>=thresholds["moderate"]["minimum_score"]: return "moderate"
    return "low"

def _resolve_rule(rules,rule_id):
    for r in rules["syndromes"]:
        if r["id"]==rule_id:return r
    return None

def _candidate(rule,score,evidence,confidence,relation_note=None):
    missing=list(rule.get("missing_if_absent",[]))
    if relation_note and relation_note not in missing:
        missing.insert(0,relation_note)
    return {
        "diagnosis":rule.get("diagnosis",rule["id"]),
        "confidence":confidence,
        "evidence_for":evidence,
        "evidence_against":[],
        "missing_discriminating_data":missing,
        "source_modules":[rule["id"]]
    }

def _dedupe_suggestions(items):
    out=[]; seen=set()
    for x in items:
        key=(x.get("action"),tuple(x.get("source_modules",[])))
        if key not in seen:
            seen.add(key); out.append(deepcopy(x))
    return out

def _problem_representation(note,top_candidates,signals):
    e=note.get("encounter",{}); age=e.get("age",{})
    if age.get("years") is not None: age_text=f"{age['years']} anos"
    elif age.get("months") is not None: age_text=f"{age['months']} meses"
    else: age_text="idade não documentada"
    sex=e.get("sex","unknown")
    complaint=note.get("history",{}).get("chief_complaint") or "motivo não documentado"
    top=", ".join(c["diagnosis"] for c in top_candidates[:2]) or "sem hipótese sindrómica suficiente"
    sig=", ".join(x[2] for x in signals[:3])
    suffix=f"; sinais relevantes: {sig}" if sig else ""
    return f"{sex}, {age_text}, {complaint}; hipóteses sindrómicas principais: {top}{suffix}."

def _active_problems(note,signals,ranked):
    problems=[]
    complaint=note.get("history",{}).get("chief_complaint")
    if complaint: problems.append(complaint)
    for _,_,label in signals: problems.append(label)
    for x in ranked[:3]:
        if x["confidence"] in {"high","moderate"}: problems.append("Suspeita: "+x["diagnosis"])
    return list(dict.fromkeys(problems))

def analyze(note, rules=None, apply_to_note=False):
    contract=diagnostic_support_contract(note)
    if contract["blocked"]:
        return {"blocked":True,"issues":contract["issues"],"assessment":None,"note":note if apply_to_note else None}
    rules=rules or load_rules()
    text=_collect_text(note)
    signals=_structured_signals(note)
    scored=[]
    for rule in rules["syndromes"]:
        score,evidence=_rule_score(rule,text,signals)
        if score>0:
            scored.append((score,rule,evidence))
    scored.sort(key=lambda x:(-x[0],x[1]["id"]))
    likely=[]; differential=[]
    for score,rule,evidence in scored:
        conf=_confidence(score,rules["qualitative_confidence"])
        cand=_candidate(rule,score,evidence,conf)
        if score>=rules["qualitative_confidence"]["moderate"]["minimum_score"]:
            likely.append(cand)
        else:
            differential.append(cand)
    # If no moderate/high syndrome, retain top low candidates only as differential.
    likely=likely[:4]
    differential=differential[:6]

    must=[]
    must_ids=[]
    for score,rule,evidence in scored[:5]:
        for rid in rule.get("must_not_miss",[]):
            if rid not in must_ids: must_ids.append(rid)
    for rid in must_ids[:5]:
        rr=_resolve_rule(rules,rid)
        if rr:
            existing=next((x for s,x,e in scored if x["id"]==rid),None)
            ev=next((e for s,x,e in scored if x["id"]==rid),[])
            sc=next((s for s,x,e in scored if x["id"]==rid),0)
            must.append(_candidate(rr,sc,ev,_confidence(max(sc,1),rules["qualitative_confidence"]),
                                   "Hipótese tempo-dependente relacionada com o síndrome principal"))

    source_rules=[]
    for score,rule,evidence in scored[:5]:
        if score>=1: source_rules.append(rule)
    suggested_tests=_dedupe_suggestions([x for r in source_rules for x in r.get("suggested_tests",[])])
    treatments=_dedupe_suggestions([x for r in source_rules for x in r.get("treatment",[])])

    # Stabilization first for objective red flags.
    if any(s[0] in {"hypotension","hipoxemia","altered_consciousness"} for s in signals):
        treatments.insert(0,{
            "action":"Priorizar abordagem ABCDE e estabilização antes de completar a documentação diagnóstica.",
            "priority":"immediate",
            "rationale":"Existem sinais objetivos potencialmente instáveis.",
            "source_modules":["undifferentiated-shock","oxygen-therapy-emergency","airway-rsi"]
        })

    limitations=[]
    if not scored:
        limitations.append("Os dados atuais não ativam nenhuma regra sindrómica com suporte suficiente.")
    limitations.append("Motor determinista baseado em regras transparentes; não é um modelo diagnóstico calibrado e não substitui revisão clínica.")
    if not note.get("complementary_tests",{}).get("laboratory"):
        limitations.append("Sem dados laboratoriais estruturados na nota.")
    contradictions=list(note.get("assessment",{}).get("contradictions_to_clarify",[]))
    for issue in contract.get("issues",[]):
        if issue.get("severity") in {"ALERT","CAUTION"}:
            contradictions.append(issue.get("message"))

    assessment={
        "problem_representation":_problem_representation(note,likely or differential,signals),
        "active_problems":_active_problems(note,signals,likely+differential),
        "likely_diagnoses":likely,
        "differential_diagnoses":differential,
        "must_not_miss":must,
        "suggested_tests":suggested_tests,
        "treatment_suggestions":treatments,
        "disposition":[{
            "action":"Definir alta, observação, internamento ou transferência após estabilização e reavaliação das hipóteses prioritárias.",
            "priority":"urgent" if likely or signals else "routine",
            "rationale":"O destino depende da gravidade, resposta ao tratamento e exclusão de diagnósticos tempo-dependentes.",
            "source_modules":["observation-discharge"]
        }],
        "reassessment":[{
            "action":"Reavaliar sinais vitais, exame dirigido e diagnóstico diferencial após novos resultados ou mudança clínica.",
            "priority":"urgent" if signals else "routine",
            "rationale":"Novos dados podem alterar a hipótese principal e o destino.",
            "source_modules":["clinical-note-diagnostic-support"]
        }],
        "contradictions_to_clarify":list(dict.fromkeys(contradictions)),
        "limitations":limitations
    }
    out_note=None
    if apply_to_note:
        out_note=deepcopy(note)
        out_note["assessment"]=assessment
        # AI-generated assessment requires clinician acceptance again.
        out_note["clinician_validation"]["reviewed"]=False
        out_note["clinician_validation"]["changes_made"]="AI/deterministic diagnostic-support assessment generated; clinician review required."
    return {
        "blocked":False,
        "issues":contract.get("issues",[]),
        "signals":[{"code":a,"weight":b,"label":c} for a,b,c in signals],
        "rule_hits":[{"module":r["id"],"score":s,"evidence":e} for s,r,e in scored],
        "assessment":assessment,
        "note":out_note
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("note_json"); p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    note=json.loads(Path(a.note_json).read_text(encoding="utf-8"))
    print(json.dumps(analyze(note,apply_to_note=a.apply),indent=2,ensure_ascii=False))
