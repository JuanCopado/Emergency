#!/usr/bin/env python3
"""Fail-closed evidence surveillance discovery runner.

Detects source changes and emits review proposals. It NEVER edits clinical
modules or the evidence registry.
"""
from __future__ import annotations
import argparse, hashlib, ipaddress, json, pathlib, socket, sys, unicodedata, urllib.request, urllib.parse
from datetime import datetime, timezone
from evidence_content_extractor import clinical_fingerprint
from evidence_change_classifier import classify
from evidence_source_gate import assess_source

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCES=ROOT/"references"/"evidence-surveillance-sources.json"

def digest(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

# Vetted discovery endpoints only. New sources require a reviewed code change.
# These hostnames do not restrict the international clinical guideline core.
APPROVED_EVIDENCE_HOSTS = frozenset({
    "normas.dgs.min-saude.pt",
    "www.ema.europa.eu",
    "www.infarmed.pt",
    "www.who.int",
    "www.erc.edu",
    "www.escardio.org",
    "www.nice.org.uk",
    "extranet.infarmed.pt",
})
MAX_EVIDENCE_RESPONSE_BYTES = 5_000_000


class _RejectRedirects(urllib.request.HTTPRedirectHandler):
    """Never contact a Location URL, including same-host or HTTPS redirects."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _validated_source_host(url):
    if not isinstance(url, str) or not url or len(url) > 4096:
        raise ValueError("Unapproved evidence source URL")
    if any(unicodedata.category(char) in {"Cc", "Cf", "Zl", "Zp"} for char in url):
        raise ValueError("Unsafe characters in evidence source URL")
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in APPROVED_EVIDENCE_HOSTS
            or parts.username is not None or parts.password is not None
            or parts.port not in (None, 443) or parts.fragment):
        raise ValueError("Unapproved evidence source destination")
    return parts.hostname


def _require_public_dns(host):
    # Additional preflight against split DNS/private IPs. TLS validates host
    # identity at connect time; DNS TOCTOU remains a deployment consideration.
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError:
        raise ValueError("Cannot resolve approved evidence source") from None
    if not addresses or any(
        not ipaddress.ip_address(item[4][0].split("%", 1)[0]).is_global
        for item in addresses
    ):
        raise ValueError("Evidence source resolved to a non-public address")


def fetch(url: str, timeout: int = 30) -> bytes:
    host = _validated_source_host(url)
    _require_public_dns(host)
    request = urllib.request.Request(
        url, headers={"User-Agent": "Emergency-Evidence-Surveillance/1.0"},
        method="GET",
    )
    # urllib's default handler follows redirects before application code can
    # inspect the final host. Explicitly disable that behavior.
    opener = urllib.request.build_opener(_RejectRedirects())
    with opener.open(request, timeout=timeout) as response:
        if getattr(response, "status", 200) != 200:
            raise RuntimeError("Evidence source returned non-success HTTP status")
        if _validated_source_host(response.geturl()) != host:
            raise ValueError("Evidence source destination changed")
        body = response.read(MAX_EVIDENCE_RESPONSE_BYTES + 1)
        if len(body) > MAX_EVIDENCE_RESPONSE_BYTES:
            raise ValueError("Evidence source response exceeds the size cap")
        return body


def run(source_path:pathlib.Path, previous:dict|None=None, cadence:str|None=None)->dict:
    cfg=json.loads(source_path.read_text(encoding="utf-8"))
    prev=(previous or {}).get("sources",{})
    out={"schema_version":2,"generated_at":datetime.now(timezone.utc).isoformat(),"production_changes_applied":False,"sources":{},"review_queue":[]}
    for s in cfg["sources"]:
        if cadence and s.get("cadence")!=cadence: continue
        gate=assess_source(s)
        item={"organization":s["organization"],"url":s["url"],"cadence":s["cadence"],"status":"error","source_gate":gate}
        if not gate["trusted_for_surveillance"]:
            item["error"]="source rejected by trust gate"
            out["sources"][s["id"]]=item
            continue
        try:
            body=fetch(s["url"])
            if len(body)>5_000_000: raise RuntimeError("response exceeds 5 MB safety cap")
            fp=clinical_fingerprint(body); h=fp["sha256"]
            old=prev.get(s["id"],{}).get("clinical_sha256") or prev.get(s["id"],{}).get("sha256")
            changed=(old is not None and old!=h)
            item.update(status="ok",clinical_sha256=h,clinical_lines=fp["clinical_lines"],changed=changed,first_observation=(old is None))
            if changed:
                triage=classify(body.decode("utf-8","replace"),s.get("domains",[]))
                proposal={"source_id":s["id"],**triage,"eligible_for_clinical_change_proposal":gate["eligible_for_clinical_change_proposal"]}
                if not gate["eligible_for_clinical_change_proposal"]:
                    proposal["classification"]="source-review-signal"
                out["review_queue"].append(proposal)
        except Exception as e:
            item["error"]=f"{type(e).__name__}: source unavailable or rejected"
        out["sources"][s["id"]]=item
    return out

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--sources",default=str(DEFAULT_SOURCES));p.add_argument("--previous");p.add_argument("--cadence",choices=["weekly","urgent"]);p.add_argument("--output",required=True)
    a=p.parse_args()
    previous=json.loads(pathlib.Path(a.previous).read_text(encoding="utf-8")) if a.previous and pathlib.Path(a.previous).exists() else None
    report=run(pathlib.Path(a.sources),previous,a.cadence)
    pathlib.Path(a.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    failures=[k for k,v in report["sources"].items() if v["status"]!="ok"]
    if failures:
        print("SURVEILLANCE INCOMPLETE; failed sources: "+", ".join(failures),file=sys.stderr);return 2
    print(f"Evidence surveillance completed; pending review: {len(report['review_queue'])}");return 0
if __name__=="__main__": raise SystemExit(main())
