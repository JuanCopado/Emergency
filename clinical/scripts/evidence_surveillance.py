#!/usr/bin/env python3
"""Fail-closed evidence surveillance discovery runner.

This runner detects source changes and emits review proposals. It NEVER edits
clinical modules or the evidence registry.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys, urllib.request\nfrom evidence_content_extractor import clinical_fingerprint
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCES=ROOT/"references"/"evidence-surveillance-sources.json"

def digest(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

def fetch(url:str, timeout:int=30)->bytes:
    req=urllib.request.Request(url, headers={"User-Agent":"Emergency-Evidence-Surveillance/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if getattr(r,"status",200)!=200: raise RuntimeError(f"HTTP {r.status}")
        return r.read(5_000_001)

def run(source_path:pathlib.Path, previous:dict|None=None)->dict:
    cfg=json.loads(source_path.read_text(encoding="utf-8"))
    prev=(previous or {}).get("sources",{})
    out={"schema_version":1,"generated_at":datetime.now(timezone.utc).isoformat(),"production_changes_applied":False,"sources":{},"review_queue":[]}
    for s in cfg["sources"]:
        item={"organization":s["organization"],"url":s["url"],"cadence":s["cadence"],"status":"error"}
        try:
            body=fetch(s["url"])
            if len(body)>5_000_000: raise RuntimeError("response exceeds 5 MB safety cap")
            fp=clinical_fingerprint(body); h=fp["sha256"]; old=prev.get(s["id"],{}).get("clinical_sha256") or prev.get(s["id"],{}).get("sha256")
            item.update(status="ok",clinical_sha256=h,clinical_lines=fp["clinical_lines"],changed=(old is not None and old!=h),first_observation=(old is None))
            if old is not None and old!=h:
                out["review_queue"].append({"source_id":s["id"],"classification":"untriaged","requires_human_review":True})
        except Exception as e:
            item["error"]=f"{type(e).__name__}: {e}"
        out["sources"][s["id"]]=item
    return out

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--sources",default=str(DEFAULT_SOURCES)); p.add_argument("--previous"); p.add_argument("--output",required=True)
    a=p.parse_args(); previous=json.loads(pathlib.Path(a.previous).read_text()) if a.previous and pathlib.Path(a.previous).exists() else None
    report=run(pathlib.Path(a.sources),previous); pathlib.Path(a.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    failures=[k for k,v in report["sources"].items() if v["status"]!="ok"]
    if failures:
        print("SURVEILLANCE INCOMPLETE; failed sources: "+", ".join(failures),file=sys.stderr); return 2
    print(f"Evidence surveillance completed; pending review: {len(report['review_queue'])}"); return 0
if __name__=="__main__": raise SystemExit(main())
