#!/usr/bin/env python3
"""Strict template gate for v1.41 procedure families already normalized."""
import pathlib,re,sys,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROC=ROOT/"modules"/"procedures"
NORMALIZED={
 "01-airway-ventilation.md":21,
 "02-vascular-monitoring.md":15,
 "03-thorax-pleura.md":10,
 "04-cardiovascular-resuscitation.md":10,
 "05-trauma-hemorrhage.md":10,
 "08-neurology.md":5,
}
REQUIRED=[
 "objetivo","indicaciones","contraindicaciones/precauciones","material","anatomía",
 "preparación","técnica paso a paso","stop","confirmación","complicaciones",
 "después","documentación","fuentes","qa"
]
HEAD=re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})",re.M)

def validate():
 errors=[];total=0
 for fn,expected in NORMALIZED.items():
  text=(PROC/fn).read_text(encoding="utf-8")
  matches=list(HEAD.finditer(text))
  if len(matches)!=expected: errors.append(f"{fn}: {len(matches)} cards != {expected}")
  for i,m in enumerate(matches):
   body=text[m.start():(matches[i+1].start() if i+1<len(matches) else len(text))].lower()
   miss=[x for x in REQUIRED if x not in body]
   if miss: errors.append(f"{m.group(1)} missing: {', '.join(miss)}")
   total+=1
 return {"normalized_cards":total,"errors":errors}

def main():
 r=validate();print(json.dumps(r,ensure_ascii=False,indent=2));return 1 if r["errors"] else 0
if __name__=="__main__": raise SystemExit(main())
