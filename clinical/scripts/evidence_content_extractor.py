#!/usr/bin/env python3
"""Conservative extraction of clinically meaningful evidence-page content."""
from __future__ import annotations
from html.parser import HTMLParser
import hashlib,re

NOISE={"script","style","nav","footer","header","aside","form","svg"}
CLINICAL_HINTS=("guideline","recommendation","dose","dosage","contraindicat","indication","treatment","diagnosis","management","safety","warning","recomendação","dose","contraindica","tratamento","diagnóstico","segurança","alerta")
class TextExtractor(HTMLParser):
 def __init__(self):
  super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag.lower() in NOISE:self.skip+=1
 def handle_endtag(self,tag):
  if tag.lower() in NOISE and self.skip:self.skip-=1
 def handle_data(self,data):
  if not self.skip:
   x=re.sub(r"\s+"," ",data).strip()
   if x:self.parts.append(x)
def canonical_text(data:bytes)->str:
 text=data.decode("utf-8","replace")
 if "<html" in text[:2000].lower() or "<!doctype html" in text[:2000].lower():
  p=TextExtractor();p.feed(text);text="\n".join(p.parts)
 lines=[]
 for line in text.splitlines():
  x=re.sub(r"\s+"," ",line).strip()
  if len(x)>=20:lines.append(x)
 return "\n".join(lines)
def clinical_fingerprint(data:bytes)->dict:
 text=canonical_text(data)
 relevant=[x for x in text.splitlines() if any(h in x.lower() for h in CLINICAL_HINTS)]
 basis="\n".join(relevant) if relevant else text
 return {"sha256":hashlib.sha256(basis.encode()).hexdigest(),"clinical_lines":len(relevant),"text_chars":len(text)}
