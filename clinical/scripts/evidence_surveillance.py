#!/usr/bin/env python3
"""Fail-closed evidence surveillance discovery runner.

Detects source changes and emits review proposals. It NEVER edits clinical
modules or the evidence registry.
"""
from __future__ import annotations
import argparse, hashlib, http.client, ipaddress, json, pathlib, socket, sys, unicodedata, urllib.request, urllib.parse
from datetime import datetime, timezone
from evidence_content_extractor import clinical_fingerprint
from evidence_change_classifier import classify
from evidence_source_gate import assess_source

ROOT=pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCES=ROOT/"references"/"evidence-surveillance-sources.json"

from cli_paths import input_file, output_file

def digest(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()

# Vetted discovery endpoints only. New sources require a reviewed code change.
# These hostnames do not restrict the international clinical guideline core.
# A catalog row may identify a source, but may not choose a network URL.
# All request destinations originate from these exact reviewed code literals.
APPROVED_EVIDENCE_URLS = {
    "dgs-portugal": "https://normas.dgs.min-saude.pt/category/normas-clinicas/",
    "ema-prac-safety-signals": "https://www.ema.europa.eu/en/human-regulatory-overview/post-authorisation/pharmacovigilance-post-authorisation/signal-management/prac-recommendations-safety-signals",
    "infarmed": "https://www.infarmed.pt/web/infarmed/alertas-de-seguranca",
    "who-guidelines": "https://www.who.int/publications/who-guidelines",
    "erc": "https://www.erc.edu/science-research/guidelines/guidelines-2025/",
    "esc-guidelines": "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines",
    "nice-guidance": "https://www.nice.org.uk/guidance/published?ndt=Guidance&ngt=Clinical+guidelines&ps=9999",
    "infarmed-fnm": "https://extranet.infarmed.pt/fnm-fo/",
}
APPROVED_EVIDENCE_HOSTS = frozenset(
    urllib.parse.urlsplit(value).hostname for value in APPROVED_EVIDENCE_URLS.values()
)
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


def _is_public_address(raw):
    if "%" in raw:
        return False
    address = ipaddress.ip_address(raw)
    mapped = getattr(address, "ipv4_mapped", None)
    if mapped is not None:
        address = mapped
    return (address.is_global and not address.is_multicast
            and not address.is_reserved and not address.is_unspecified
            and not address.is_loopback and not address.is_link_local)


def _require_public_dns(host):
    # Reject mixed public/private answers before any connection. The transport
    # below connects to a validated numeric address and keeps TLS SNI/host checks.
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError:
        raise ValueError("Cannot resolve approved evidence source") from None
    if not addresses or any(
        not _is_public_address(item[4][0])
        for item in addresses
    ):
        raise ValueError("Evidence source resolved to a non-public address")
    return tuple(dict.fromkeys(item[4][0] for item in addresses))


class _PublicHTTPSConnection(http.client.HTTPSConnection):
    """Pin the actual socket to a vetted DNS answer, preserving TLS identity."""

    def connect(self):
        if self._tunnel_host:
            raise ValueError("Evidence source proxy tunnels are forbidden")
        addresses = _require_public_dns(self.host)
        last_error = None
        for address in addresses:
            raw = None
            try:
                raw = socket.create_connection((address, 443), self.timeout,
                                               self.source_address)
                self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
                return
            except OSError as exc:
                if raw is not None:
                    raw.close()
                last_error = exc
        raise OSError("Approved evidence source connection failed") from last_error


class _PublicHTTPSHandler(urllib.request.HTTPSHandler):
    def https_open(self, request):
        return self.do_open(_PublicHTTPSConnection, request,
                            context=self._context)


def fetch(source_id: str, configured_url: str, timeout: int = 30) -> bytes:
    # The untrusted catalog URL is only compared for provenance consistency;
    # it is never passed into urllib's request constructor.
    canonical_url = APPROVED_EVIDENCE_URLS.get(source_id)
    if canonical_url is None or configured_url != canonical_url:
        raise ValueError("Unapproved evidence source identity or URL")
    host = _validated_source_host(canonical_url)
    _require_public_dns(host)
    request = urllib.request.Request(
        canonical_url, headers={"User-Agent": "Emergency-Evidence-Surveillance/1.0"},
        method="GET",
    )
    # urllib's default handler follows redirects before application code can
    # inspect the final host. Explicitly disable that behavior.
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), _RejectRedirects(), _PublicHTTPSHandler())
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
            body=fetch(s["id"], s["url"])
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

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=pathlib.Path, default=DEFAULT_SOURCES)
    parser.add_argument("--previous", type=pathlib.Path)
    parser.add_argument("--cadence", choices=["weekly", "urgent"])
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    # Validate every supplied path before business processing. The launcher grants the roots.
    try:
        if args.sources is DEFAULT_SOURCES:
            args.sources = DEFAULT_SOURCES
        else:
            args.sources = input_file(args.sources)
        if args.previous is not None:
            args.previous = input_file(args.previous)
        args.output = output_file(args.output)
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))
    destination: pathlib.Path = output_file(args.output)
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
    report = run(args.sources, previous, args.cadence)
    destination.write_text(data=json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    failures = [key for key, value in report["sources"].items() if value["status"] != "ok"]
    if failures:
        print("SURVEILLANCE INCOMPLETE; failed sources: " + ", ".join(failures), file=sys.stderr)
        return 2
    print(f"Evidence surveillance completed; pending review: {len(report['review_queue'])}")
    return 0

if __name__=="__main__": raise SystemExit(main())
