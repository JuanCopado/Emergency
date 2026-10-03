#!/usr/bin/env python3
"""Source-encoded CORE transversal tools."""

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
