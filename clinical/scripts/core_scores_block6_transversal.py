#!/usr/bin/env python3
"""Source-encoded CORE transversal tools."""

from clinical_calculator import calculate as calculate_formula

AVPU_ORDER={"alert":0,"voice":1,"pain":2,"unresponsive":3}

def calculate_avpu(data):
    state=data.get("state")
    if state is None:
        raise ValueError("AVPU state required")
    key=str(state).strip().lower()
    aliases={"a":"alert","v":"voice","p":"pain","u":"unresponsive","vocal":"voice"}
    key=aliases.get(key,key)
    if key not in AVPU_ORDER:
        raise ValueError("AVPU state must be alert/voice/pain/unresponsive")
    return {
      "id":"avpu","status":"complete","state":key,"ordinal":AVPU_ORDER[key],
      "warning":"AVPU is a rapid consciousness assessment. Any depressed level requires clinical evaluation; use GCS or another structured neurologic assessment when greater detail is needed.",
      "source":{
        "authority":"Resuscitation Council UK",
        "url":"https://www.resus.org.uk/library/abcde-approach",
        "version":"ABCDE/AVPU",
      },
    }

def calculate_shock_index(data):
    value,unit=calculate_formula("shock-index-formula",data)
    return {
      "id":"shock-index","status":"complete","value":value,"unit":unit,
      "formula_alias":"shock-index-formula",
      "warning":"Shock Index is HR/SBP and is context-dependent; it is not a stand-alone diagnosis of shock and adult cutoffs should not be applied to children.",
      "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6698590/","version":"Shock Index review"},
    }

def calculate_modified_shock_index(data):
    value,unit=calculate_formula("modified-shock-index-formula",data)
    return {
      "id":"modified-shock-index","status":"complete","value":value,"unit":unit,
      "formula_alias":"modified-shock-index-formula",
      "warning":"Modified Shock Index is HR/MAP and is an adjunct, not a stand-alone diagnosis or treatment rule.",
      "source":{"url":"https://pmc.ncbi.nlm.nih.gov/articles/PMC6698590/","version":"Modified Shock Index"},
    }
