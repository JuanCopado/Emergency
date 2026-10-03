#!/usr/bin/env python3
"""Source-encoded Pediatric Glasgow Coma Scale."""

EYE={"spontaneous":4,"to_voice":3,"to_pain":2,"none":1}
MOTOR={"obeys_or_normal_spontaneous":6,"localizes_pain":5,"withdraws_pain":4,"abnormal_flexion":3,"extension":2,"none":1}
VERBAL_4_PLUS={"oriented":5,"confused":4,"inappropriate_words":3,"incomprehensible_sounds":2,"none":1}
VERBAL_UNDER4={"alert_babbles_coos_words_usual":5,"less_than_usual_words_or_irritable_cry":4,"cries_only_to_pain":3,"moans_to_pain":2,"none":1}

SOURCE={
 "authority":"Royal Children's Hospital Melbourne",
 "url":"https://www.rch.org.au/clinicalguide/guideline_index/Altered_conscious_state/",
 "version":"Paediatric GCS >=4 years / <4 years",
}

def _cat(value,mapping,name):
    if isinstance(value,str):
        key=value.strip().lower()
        if key in {"nt","not_testable","untestable"}: return None
        if key not in mapping: raise ValueError(f"{name}: unsupported category")
        return mapping[key]
    if isinstance(value,bool) or not isinstance(value,int) or value not in set(mapping.values()):
        raise ValueError(f"{name}: invalid score/category")
    return value

def calculate_pediatric_gcs(data):
    if data.get("age_years") is None: raise ValueError("age_years required")
    age=float(data["age_years"])
    if age<0 or age>=18: raise ValueError("pediatric-gcs requires age 0 to <18 years")
    for k in ("eye","verbal","motor"):
        if data.get(k) is None: raise ValueError(f"missing pediatric GCS component: {k}")
    eye=_cat(data["eye"],EYE,"eye")
    motor=_cat(data["motor"],MOTOR,"motor")
    verbal_map=VERBAL_UNDER4 if age<4 else VERBAL_4_PLUS
    verbal=_cat(data["verbal"],verbal_map,"verbal")
    components={"E":eye,"V":verbal,"M":motor}
    if any(v is None for v in components.values()):
        return {
          "id":"pediatric-gcs","status":"not_testable_component_present",
          "age_band":"under_4" if age<4 else "4_or_more",
          "components":components,"total":None,
          "warning":"Record E/V/M separately; do not impute a total when a component is not testable.",
          "source":SOURCE,
        }
    total=eye+verbal+motor
    return {
      "id":"pediatric-gcs","status":"complete",
      "age_band":"under_4" if age<4 else "4_or_more",
      "components":components,"total":total,"range":[3,15],
      "display":f"E{eye} V{verbal} M{motor} = {total}/15",
      "source":SOURCE,
    }
