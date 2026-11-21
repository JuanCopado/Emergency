#!/usr/bin/env python3
"""Transparent deterministic diagnostic-support engine for structured clinical notes.

This engine is not a calibrated diagnostic model. It applies explicit, inspectable
rules to privacy-cleared note content and routes recommendations to existing modules.
"""

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import NamedTuple

from clinical_note_support import diagnostic_support_contract

ROOT=Path(__file__).parents[1]
RULES_PATH=ROOT/"qa"/"clinical-note-diagnostic-rules.json"

from cli_paths import input_file

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

def _collect_text(note, include_history=False):
    parts=[]
    h=note.get("history",{})
    for key in ("chief_complaint","present_illness","social_history","baseline_status"):
        if h.get(key): parts.append(h[key])
    history_keys = ("past_medical_history", "past_surgical_history") if include_history else ()
    for key in (*history_keys, "medication_discrepancies"):
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
    return _norm(" | ".join(str(x).replace("\n", " | ") for x in parts if x))

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

# Bounded, inspectable context rules, not a general clinical NLP parser.
# Boundaries keep one symptom/field's context from suppressing another clause.
_CONTEXT_BOUNDARY = re.compile(
    r"[.;!?|\n]|\b(?:pero|mas|but|however|porem|contudo|sin embargo|no entanto)\b|"
    r",\s*(?=(?:now|currently|ahora|agora|actualmente|atualmente|"
    r"(?:the )?patient (?:has|reports|denies)|(?:el |o )?paciente (?:tiene|tem|refiere|refere)|"
    r"(?:ecg|ekg) (?:shows|demonstrates|muestra|mostra))\b)"
)
_NEGATION = re.compile(
    r"\b(?:no|nao|not|niega|nega|denies|denied|sin|sem|without|"
    r"ausencia de|absence of)\b"
)
_CURRENT = re.compile(
    r"\b(?:actualmente|ahora|agora|currently|now|ongoing|presenta|apresenta|"
    r"persiste|persistem|persists|persistente|persistent)\b"
)
_PSEUDO_NEGATION = re.compile(
    r"^\s*(?:solo|so|apenas|only|se descarta|se puede descartar|se pode excluir|"
    r"ecg|monitor|exame|relatorio)\b"
)
_POST_NEGATION = re.compile(r"^\s*(?:,\s*)?(?:(?:is|esta|was)\s+)?(?:denied|negad[oa]|ausente|absent)\b")
_PAST = re.compile(
    r"\b(?:antecedentes?(?: de)?|historia de|history of|previously|previamente|"
    r"anteriormente|tuvo|teve|presento previamente|ayer|ontem)\b"
)
_TIME_AGO = re.compile(
    r"\b(?:hace|ha)\s+(?:\d+|un|una|uno|um|uma|dos|dois|two|three)\s+"
    r"(?:dias?|anos?|semanas?|meses)\b|\b\d+\s+(?:days?|years?|weeks?|months?)\s+ago\b"
)
_RESOLVED = re.compile(r"^\s*(?:,\s*)?(?:(?:is|esta|was|ya|ja|already)\s+)*(?:resuelt[oa]|resolvid[oa]|resolved)\b")
_UNCERTAIN = re.compile(
    r"\b(?:possib(?:le|ly)|posible|possivel|suspected|suspeita de|sospecha de|"
    r"cannot (?:exclude|rule out)|can(?:not|'t) rule out|rule out|"
    r"no se (?:puede descartar|descarta)|nao se pode (?:excluir|descartar)|"
    r"nao se exclui|pendiente de confirmar|pendente de confirmar|a descartar|a excluir)\b"
)
_OTHER_SUBJECT = re.compile(
    r"\b(?:family history|antecedentes familiares|historia familiar|"
    r"(?:mother|father|sister|brother) (?:has|had|with|denies)|"
    r"(?:madre|padre|herman[oa]|mae|pai|irmao|irma) (?:con|com|tem|tiene|apresenta|presenta))\b"
)
_DIRECT_DENIAL = re.compile(r"\b(?:denies|denied|niega|nega|sin|sem|without|no|not|ausencia de|absence of)\s*$")


def _mention_context(before, after):
    """Classify context around one occurrence; cues inside the term are ignored."""
    prefix = _CONTEXT_BOUNDARY.split(before)[-1]
    suffix = _CONTEXT_BOUNDARY.split(after)[0]
    current = list(_CURRENT.finditer(prefix))
    last_current = current[-1] if current else None
    negated = False
    for cue in _NEGATION.finditer(prefix):
        following = prefix[cue.end():]
        if _PSEUDO_NEGATION.match(following):
            continue
        if len(re.findall(r"\b\w+\b", following)) > 8:
            continue
        # "no presenta fiebre" stays negated; "niega fiebre, presenta dolor"
        # starts a new assertion. This also handles an explicit "ahora/agora".
        if last_current and last_current.start() > cue.end():
            between = prefix[cue.end():last_current.start()]
            if re.search(r"\w", between):
                continue
        negated = True
    negated = negated or bool(_POST_NEGATION.match(suffix))
    past = list(_PAST.finditer(prefix))
    for cue in _TIME_AGO.finditer(prefix):
        if not re.search(r"\bdesde\s*$", prefix[:cue.start()]):
            past.append(cue)
    historical = any(
        len(re.findall(r"\b\w+\b", prefix[cue.end():])) <= 16
        and (last_current is None or cue.start() > last_current.start())
        for cue in past
    )
    # A nearby postposed date applies to this mention, not to a later clause.
    local_suffix = suffix.split(",", 1)[0]
    for cue in _TIME_AGO.finditer(local_suffix):
        if (last_current is None and not _CURRENT.search(local_suffix[:cue.start()])
                and not re.search(r"\bdesde\s*$", local_suffix[:cue.start()])
                and len(re.findall(r"\b\w+\b", local_suffix[:cue.start()])) <= 6):
            historical = True
    historical = historical or bool(_RESOLVED.match(suffix))
    # Attribute only direct denials to the patient. A broad negation scope
    # can suppress a trigger without supplying evidence against it.
    direct_denial = bool(_DIRECT_DENIAL.search(prefix) or _POST_NEGATION.match(suffix))
    speculative = bool(
        _UNCERTAIN.search(prefix)
        or re.match(r"^\s*\?", after)
        or re.match(r"^\s*(?:is\s+)?(?:possible|suspected|por confirmar|a confirmar)\b", suffix)
    )
    return negated, historical, direct_denial, speculative, bool(_OTHER_SUBJECT.search(prefix))


def _term_states(term, text, allow_historical=False):
    """Classify all occurrences in already normalized text."""
    t=_norm(term)
    if not t:
        return set()
    # Short standalone acronyms/tokens (e.g. TEN, VF, PEA, AKI, DT) must
    # not match inside ordinary words such as "extremidades" or "paciente".
    pattern = re.escape(t)
    if re.fullmatch(r"[a-z0-9]+",t) and len(t)<=4:
        pattern = r"(?<![a-z0-9])" + pattern + r"(?![a-z0-9])"
    states = set()
    for match in re.finditer(pattern, text):
        negated, historical, direct, speculative, other_subject = _mention_context(text[:match.start()], text[match.end():])
        if other_subject or (historical and not allow_historical):
            continue
        if speculative:
            states.add("uncertain")
        if not negated and speculative:
            states.add("unconfirmed_match")
        elif not negated:
            states.add("present")
        elif direct and not historical and not speculative:
            states.add("denied")
    return states

def _term_present(term, text, allow_historical=False):
    return "present" in _term_states(term, _norm(text.replace("\n", " | ")), allow_historical)

class RuleObservation(NamedTuple):
    score: int
    evidence: list
    denied: list
    uncertain: list
    weighted_uncertainty: list


def _rule_score(rule,text,signals,historical_text=None):
    score=0; evidence=[]; denied=[]; uncertain=[]; weighted_uncertainty=[]
    signal_names={x[0] for x in signals}
    signal_labels={x[0]:x[2] for x in signals}
    for trig in rule.get("triggers",[]):
        t=trig.get("type")
        if t=="text_any":
            allow_historical = trig.get("allow_historical") is True
            source_text = historical_text if allow_historical and historical_text is not None else text
            present = False
            unconfirmed_matches = []
            for term in trig.get("terms", []):
                states = _term_states(term, source_text, allow_historical)
                present |= "present" in states
                if "unconfirmed_match" in states:
                    unconfirmed_matches.append(term)
                if "uncertain" in states:
                    uncertain.append(term)
                if "denied" in states:
                    denied.append("Negado: " + term)
            # Keep the established weighting of mixed notes until adjudication.
            # An uncertain mention is never printed as observed evidence.
            if present or unconfirmed_matches:
                score += int(trig.get("weight",1))
            if present:
                evidence.append(trig.get("label") or "hallazgo textual")
            else:
                weighted_uncertainty.extend(unconfirmed_matches)
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
    return RuleObservation(score if evidence else 0, list(dict.fromkeys(evidence)), list(dict.fromkeys(denied)),
                           list(dict.fromkeys(uncertain)), list(dict.fromkeys(weighted_uncertainty)) if evidence else [])

def _confidence(score, thresholds):
    if score>=thresholds["high"]["minimum_score"]: return "high"
    if score>=thresholds["moderate"]["minimum_score"]: return "moderate"
    return "low"

def _resolve_rule(rules,rule_id):
    for r in rules["syndromes"]:
        if r["id"]==rule_id:return r
    return None

def _documented_discriminants(note):
    """Match only typed, unequivocal individual fields, never a compound request."""
    vitals = _latest_vitals(note)
    documented = {}
    if _age_years(note) is not None:
        documented["idade"] = None
    if vitals.get("spo2") is not None and 0 <= vitals["spo2"] <= 100:
        documented["SpO2"] = None
    if vitals.get("rr") is not None and vitals["rr"] >= 0:
        documented["frequência respiratória"] = None
    if re.fullmatch(r"(?:[3-9]|1[0-5])", str(vitals.get("gcs", "")).strip()):
        documented["GCS"] = None
    if any(report.get("provenance") == "official_report"
           and (report.get("official_report") or "").strip()
           for report in note.get("complementary_tests", {}).get("ecg", [])):
        documented["ECG"] = "ECG: relatório oficial registado; verificar conteúdo e adequação."
    return documented

def _candidate(rule,score,evidence,confidence,relation_note=None,*,observation=None,documented=None):
    documented = documented or {}
    missing = [documented.get(item, item) for item in rule.get("missing_if_absent", [])]
    missing = [item for item in missing if item is not None]
    if relation_note and relation_note not in missing:
        missing.insert(0,relation_note)
    return {
        "diagnosis":rule.get("diagnosis",rule["id"]),
        "confidence":confidence,
        "evidence_for":evidence,
        "evidence_against":list(observation.denied) if observation else [],
        **({"weighted_uncertainty":list(observation.weighted_uncertainty)}
           if observation and observation.weighted_uncertainty else {}),
        "missing_discriminating_data":missing,
        "source_modules":list(rule.get("source_modules", [rule["id"]]))
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
    historical_text=_collect_text(note, include_history=True)
    signals=_structured_signals(note)
    scored=[]
    observations = {}
    documented = _documented_discriminants(note)
    age_years=_age_years(note)
    for rule in rules["syndromes"]:
        if age_years is not None:
            if rule.get("min_age_years") is not None and age_years < float(rule["min_age_years"]):
                continue
            if rule.get("max_age_years") is not None and age_years > float(rule["max_age_years"]):
                continue
        observation = _rule_score(rule,text,signals,historical_text)
        observations[rule["id"]] = observation
        if observation.score > 0:
            scored.append((observation.score,rule,observation.evidence))
    scored.sort(key=lambda x:(-x[0],x[1]["id"]))
    likely=[]; differential=[]
    for score,rule,evidence in scored:
        conf=_confidence(score,rules["qualitative_confidence"])
        cand=_candidate(rule,score,evidence,conf,observation=observations[rule["id"]],documented=documented)
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
    limitations=[]
    uncertain_terms = list(dict.fromkeys(term for obs in observations.values() for term in obs.uncertain))
    if uncertain_terms:
        limitations.append("Menções incertas que o motor pode pontuar: " + ", ".join(uncertain_terms)
                           + ". Não estão confirmadas e exigem revisão médica.")
    for rid in must_ids:
        rr=_resolve_rule(rules,rid)
        if rr is None:
            limitations.append(f"Relação prioritária sem regra avaliável: {rid}. Requer revisão médica.")
        elif rid in observations and len(must) < 5:
            obs = observations[rid]
            must.append(_candidate(rr,obs.score,obs.evidence,_confidence(max(obs.score,1),rules["qualitative_confidence"]),
                                   "Hipótese tempo-dependente relacionada com o síndrome principal",
                                   observation=obs,documented=documented))
        else:
            limitations.append(f"Relação prioritária não apresentada para este contexto: {rid}.")

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
    p.add_argument("note_json", type=Path); p.add_argument("--apply",action="store_true")
    a=p.parse_args()
    # Validate every supplied path before business processing. The launcher grants the roots.
    try:
        a.note_json = input_file(a.note_json)
    except argparse.ArgumentTypeError as error:
        p.error(str(error))
    note=json.loads(a.note_json.read_text(encoding="utf-8"))
    print(json.dumps(analyze(note,apply_to_note=a.apply),indent=2,ensure_ascii=False))
