#!/usr/bin/env python3
"""Structural validator for v1.41 emergency procedure cards.

This is a documentation-quality gate, not a clinical-validity gate.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC_DIR = ROOT / "modules" / "procedures"
HEADER = re.compile(r"^##\s+(PROC-[A-Z]+-\d{3})\s+—\s+(.+?)(?:\s+—\s+([A-Z/]+))?$", re.M)
MIN_BODY = 90

def validate():
    errors = []
    warnings = []
    cards = {}
    for path in sorted(PROC_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        matches = list(HEADER.finditer(text))
        for i,m in enumerate(matches):
            proc_id,title,level=m.group(1),m.group(2).strip(),(m.group(3) or "")
            body=text[m.end():(matches[i+1].start() if i+1<len(matches) else len(text))].strip()
            if "REFERENCIA" in level:
                if "Ver **PROC-" not in body:
                    errors.append(f"{proc_id}: reference alias lacks canonical target")
                continue
            if proc_id in cards:
                errors.append(f"{proc_id}: duplicate canonical card")
            cards[proc_id]=(path.name,title,level,body)
            if len(body) < MIN_BODY:
                errors.append(f"{proc_id}: body too short ({len(body)} chars)")
            lower=body.lower()
            if not any(k in lower for k in ("técnica", "flujo", "secuencia", "contenido ed", "opciones")):
                warnings.append(f"{proc_id}: no explicit technique/flow label")
            if level in {"ADVANCED","SPECIALIST"} and not any(k in body for k in ("**STOP:**","**STOP", "riesgo", "Riesgo", "complic")):
                warnings.append(f"{proc_id}: advanced/specialist card lacks explicit STOP/risk language")
            if "**Visual:**" not in body and "Ver **PROC-" not in body:
                warnings.append(f"{proc_id}: no explicit visual brief line")
    if len(cards) != 192:
        errors.append(f"canonical card count {len(cards)} != 192")
    return {"canonical_cards":len(cards),"errors":errors,"warnings":warnings}

def main():
    report=validate()
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report["errors"] else 0

if __name__=="__main__":
    raise SystemExit(main())
