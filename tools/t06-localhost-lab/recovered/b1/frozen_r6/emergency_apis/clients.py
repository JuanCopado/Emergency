"""Offline-only research gateway for PubMed, Europe PMC, and NVD.

Public networking remains disabled, including when allow_network=True.
Only caller-provided synthetic transports may be used for tests.
This package is not a clinical decision-support service.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import hmac
import http.client
import json
from types import MappingProxyType
import math
import os
from pathlib import Path
import re
import secrets
import stat
import threading
import time
import unicodedata
from typing import Callable, Mapping
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit


class APIGatewayError(RuntimeError):
    """Safe gateway error: intentionally excludes request URLs, queries and keys."""


class ValidationError(APIGatewayError):
    pass


class NetworkDisabled(APIGatewayError):
    pass


@dataclass(frozen=True)
class HTTPReply:
    status: int
    body: bytes
    headers: Mapping[str, str]


@dataclass(frozen=True)
class APIResult:
    service: str
    records: list[dict]
    total: int | None
    provenance: dict

    def as_dict(self) -> dict:
        return asdict(self)


# Trusted fixed routes; not caller-supplied URL inputs.
ENDPOINTS = MappingProxyType({
    "pubmed": ("eutils.ncbi.nlm.nih.gov", "/entrez/eutils/esearch.fcgi"),
    "europe_pmc": ("www.ebi.ac.uk", "/europepmc/webservices/rest/search"),
    "nvd": ("services.nvd.nist.gov", "/rest/json/cves/2.0"),
})

# Conservative single-process rates, not a guarantee of aggregate compliance.
MIN_INTERVAL_SECONDS = MappingProxyType({"pubmed": 0.36, "europe_pmc": 1.0, "nvd": 7.0})
RETRYABLE = frozenset({429, 500, 502, 503, 504})


MAX_RESPONSE_BYTES = 2_000_000
# Signed cache envelope includes metadata/HMAC around the validated HTTP JSON.
# A separate hard cap avoids losing otherwise-valid near-limit responses.
MAX_CACHE_ENVELOPE_BYTES = MAX_RESPONSE_BYTES + 4096
MAX_RECORDS = 50
BLOCKED_UNICODE_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Zl", "Zp"})
CLIENT_VERSION = "0.7.0-R6-transport-contract-candidate"

# PRE-REVIEWED PUBLIC TOPIC VALUES. Never use user-entered free text in a live API.
# For additional topics, a reviewer must change this versioned catalog in code.
APPROVED_PUBLIC_QUERIES = MappingProxyType({
    "pubmed": frozenset({"shock", "sepsis", "septic shock systematic review", "emergency medicine"}),
    "europe_pmc": frozenset({"shock", "sepsis", "emergency medicine"}),
    "nvd": frozenset({"vite", "openssl", "libcurl"}),
})


def _canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def _get_hmac_key(explicit_key: bytes | str | None, *, persistent_cache: bool) -> bytes:
    """Load binary secret, rejecting obvious weak keys without claiming to measure entropy.

    Configure EMERGENCY_AUDIT_HMAC_KEY as hex:<64 or more hex digits> generated
    by a CSPRNG. Strings without this representation are rejected to avoid
    accidentally accepting copied phrases/passwords. A syntax/diversity gate
    cannot establish cryptographic unpredictability; secret generation and
    permissions remain external deployment obligations.
    """
    value = explicit_key if explicit_key is not None else os.environ.get("EMERGENCY_AUDIT_HMAC_KEY")
    if value is None:
        if persistent_cache:
            raise ValidationError("Persistent cache requires a configured HMAC key")
        return secrets.token_bytes(32)
    if isinstance(value, str):
        if not re.fullmatch(r"hex:(?:[0-9A-Fa-f]{2}){32,64}", value, flags=re.ASCII):
            raise ValidationError("Audit HMAC key string must be hex-encoded CSPRNG bytes")
        value = bytes.fromhex(value[4:])
    if (not isinstance(value, bytes) or len(value) < 32 or
            len(set(value)) < 12 or not value.strip()):
        raise ValidationError("Audit HMAC key is too short or obviously low diversity")
    return value


def _cache_supported_platform() -> bool:
    # Fail closed: Windows cache stays disabled until independent ACL validation.
    return os.name == "posix" and callable(getattr(os, "getuid", None))


def _safe_posix_cache_metadata(meta, *, is_dir: bool) -> bool:
    """Guard all POSIX-only ownership checks in one fail-closed boundary."""
    getuid = getattr(os, "getuid", None)
    if os.name != "posix" or not callable(getuid):
        return False
    if is_dir and not stat.S_ISDIR(meta.st_mode):
        return False
    if not is_dir and not stat.S_ISREG(meta.st_mode):
        return False
    return meta.st_uid == getuid() and (meta.st_mode & 0o077) == 0



def _read_capped(stream, timeout: float) -> bytes:
    """Bound response bytes and total monotonic elapsed time (not only socket operations).

    Retained only for bounded synthetic-stream regression testing. This does
    not supply a network transport and is NOT a global DNS/TCP/TLS deadline.
    """
    deadline = time.monotonic() + timeout
    chunks: list[bytes] = []
    size = 0
    fp = getattr(stream, "fp", None)
    sock = getattr(getattr(fp, "raw", None), "_sock", None)
    while size <= MAX_RESPONSE_BYTES:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise APIGatewayError("API response exceeded total read deadline")
        if sock is not None:
            try:
                sock.settimeout(remaining)
            except (OSError, AttributeError, ValueError):
                pass
        # Let transport exceptions bubble to APIClient.search() for bounded
        # retries and safe replacement messages. No URLs or keys are logged.
        reader = getattr(stream, "read1", None) or stream.read
        chunk = reader(min(65536, MAX_RESPONSE_BYTES + 1 - size))
        if time.monotonic() > deadline:
            raise APIGatewayError("API response exceeded total read deadline")
        if not chunk:
            return b"".join(chunks)
        if not isinstance(chunk, bytes):
            raise APIGatewayError("Unexpected API response body type")
        size += len(chunk)
        chunks.append(chunk)
    raise APIGatewayError("API response exceeds safety limit")


def _has_unsafe_controls(value: str) -> bool:
    return any(unicodedata.category(c) in BLOCKED_UNICODE_CATEGORIES for c in value)


def _text(value, *, max_len: int = 1200) -> str | None:
    """Type- and length-bound external strings. They remain UNTRUSTED text.

    Do not interpret as HTML or inject into prompts without a downstream gate.
    """
    if not isinstance(value, str):
        return None
    if _has_unsafe_controls(value):
        raise APIGatewayError("External text contains disallowed characters")
    return value[:max_len]


def _int_or_none(value) -> int | None:
    if type(value) is int and 0 <= value < 1_000_000_000_000:
        return value
    if isinstance(value, str) and re.fullmatch(r"[0-9]{1,12}", value, flags=re.ASCII):
        return int(value)
    return None


def _reject_nonfinite_constant(_value: str):
    raise ValueError("Nonfinite JSON numbers are forbidden")


def _parse_finite_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Nonfinite JSON numbers are forbidden")
    return result


def _safe_json_loads(raw: bytes) -> dict:
    try:
        result = json.loads(raw.decode("utf-8"), parse_constant=_reject_nonfinite_constant,
                            parse_float=_parse_finite_float)
    except (UnicodeError, ValueError, RecursionError, OverflowError):
        raise APIGatewayError("API response is not valid bounded UTF-8 JSON") from None
    if not isinstance(result, dict):
        raise APIGatewayError("Unexpected API response type")
    return result


def _validate_query(query: str) -> str:
    if not isinstance(query, str) or not (2 <= len(query.strip()) <= 200):
        raise ValidationError("Query must contain 2–200 characters")
    clean = query.strip()
    if (_has_unsafe_controls(clean) or "@" in clean or
            re.search(r"\b(?:DOB|MRN|SSN|patient\s*id|DNI|NIF|NIE|NHC|CIP|historia\s*cl[ií]nica|paciente|fecha\s*de\s*nacimiento|nacido|nacida|telem[oó]vel|tel[eé]fono|morada|direcci[oó]n)\b", clean, re.I) or
            re.search(r"(?<![0-9])[0-9]{6,}(?![0-9])", clean, re.ASCII) or
            re.search(r"\b[0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}\b|\b[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{4}\b", clean, re.ASCII)):
        raise ValidationError("Query contains unsupported or potentially sensitive content")
    return clean


def _validate_approved_query(service: str, clean: str) -> None:
    # PHI detection cannot be guaranteed by regex. Only exact audited topics pass.
    if clean not in APPROVED_PUBLIC_QUERIES[service]:
        raise ValidationError("Query is not in the approved public-topic catalog")


def _validate_response(reply: HTTPReply) -> dict:
    if len(reply.body) > MAX_RESPONSE_BYTES:
        raise APIGatewayError("API response exceeds safety limit")
    if reply.status != 200:
        raise APIGatewayError(f"Remote service returned HTTP {int(reply.status)}")
    return _safe_json_loads(reply.body)


def _validate_transport_reply(reply: object) -> HTTPReply:
    """Fail closed on malformed injected-transport responses (audit R5-01).

    Do not expose raw headers, response bodies or repr(reply) in errors.
    This validation does not enable networking or authorize any HTTP client.
    """
    if (not isinstance(reply, HTTPReply) or type(reply.status) is not int or
            not 100 <= reply.status <= 599 or type(reply.body) is not bytes or
            not isinstance(reply.headers, Mapping)):
        raise APIGatewayError("Invalid transport reply")
    try:
        for name, value in reply.headers.items():
            if (not isinstance(name, str) or not isinstance(value, str) or
                    not 1 <= len(name) <= 128 or len(value) > 2048 or
                    _has_unsafe_controls(name) or _has_unsafe_controls(value)):
                raise APIGatewayError("Invalid transport reply")
    except (AttributeError, TypeError, ValueError, RuntimeError):
        raise APIGatewayError("Invalid transport reply") from None
    return reply


def _records(service: str, data: dict) -> tuple[list[dict], int | None]:
    if service == "pubmed":
        response = data.get("esearchresult")
        if not isinstance(response, dict) or not isinstance(response.get("idlist"), list):
            raise APIGatewayError("Unexpected PubMed response schema")
        ids = response["idlist"]
        if len(ids) > MAX_RECORDS or any(not isinstance(x, str) or not re.fullmatch(r"[0-9]{1,9}", x, re.ASCII) for x in ids):
            raise APIGatewayError("Invalid PubMed identifier")
        records = [{"pmid": x, "article_url": f"https://pubmed.ncbi.nlm.nih.gov/{x}/"} for x in ids]
        total = _int_or_none(response.get("count"))
        return records, total
    if service == "europe_pmc":
        rlist = data.get("resultList")
        if not isinstance(rlist, dict) or not isinstance(rlist.get("result"), list):
            raise APIGatewayError("Unexpected Europe PMC response schema")
        records = []
        if len(rlist["result"]) > MAX_RECORDS:
            raise APIGatewayError("API returned too many records")
        for item in rlist["result"]:
            if not isinstance(item, dict):
                raise APIGatewayError("Unexpected Europe PMC item")
            records.append({
                "id": _text(item.get("id"), max_len=80),
                "source": _text(item.get("source"), max_len=40),
                "title": _text(item.get("title"), max_len=1200),
                "author_string": _text(item.get("authorString"), max_len=500),
                "pub_year": _text(item.get("pubYear"), max_len=4),
                "journal": _text(item.get("journalTitle"), max_len=300),
                "pmid": _text(item.get("pmid"), max_len=20),
                "doi": _text(item.get("doi"), max_len=300),
            })
        total = _int_or_none(data.get("hitCount"))
        return records, total
    items = data.get("vulnerabilities")
    if not isinstance(items, list):
        raise APIGatewayError("Unexpected NVD response schema")
    if len(items) > MAX_RECORDS:
        raise APIGatewayError("API returned too many records")
    records = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("cve"), dict):
            raise APIGatewayError("Unexpected NVD item")
        cve = item["cve"]
        cve_id = cve.get("id")
        if not isinstance(cve_id, str) or not re.fullmatch(r"CVE-[0-9]{4}-[0-9]{4,12}", cve_id, flags=re.ASCII):
            raise APIGatewayError("Invalid CVE identifier")
        descriptions = cve.get("descriptions")
        desc = next((x.get("value") for x in descriptions if isinstance(x, dict) and x.get("lang") == "en"), None) if isinstance(descriptions, list) else None
        records.append({"cve_id": cve_id, "published": _text(cve.get("published"), max_len=60),
                        "last_modified": _text(cve.get("lastModified"), max_len=60),
                        "description_en": _text(desc, max_len=1800),
                        "cve_url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"})
    total = _int_or_none(data.get("totalResults"))
    return records, total


class APIClient:
    """Read-only client. This is a research/engineering interface, NOT a clinical engine.

    Transport may be dependency-injected for offline testing. Default network mode is OFF.
    Cache contents are untrusted and are still schema-validated on read.
    """

    def __init__(self, *, allow_network: bool = False,
                 transport: Callable[[str, Mapping[str, str], float], HTTPReply] | None = None,
                 cache_dir: str | Path | None = None, ttl_seconds: int = 3600,
                 timeout_seconds: float = 10.0, retries: int = 2,
                 hmac_key: bytes | str | None = None,
                 clock: Callable[[], float] = time.monotonic,
                 wall_clock: Callable[[], float] = time.time,
                 sleeper: Callable[[float], None] = time.sleep):
        # No real network in R6: absolute DNS/TCP/TLS deadlines, secrets, and
        # egress/proxy redaction require independent verification first.
        if transport is None:
            self.transport = None
        else:
            self.transport = transport  # Test/integration injection only.
        if not (1 <= ttl_seconds <= 604800 and 1 <= timeout_seconds <= 30 and 0 <= retries <= 3):
            raise ValidationError("Invalid cache, timeout or retry configuration")
        self.allow_network = False  # R6 stays offline, even when allow_network=True.
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir is not None and not _cache_supported_platform():
            raise ValidationError("Disk cache disabled on this platform pending ACL audit")
        self._hmac_key = _get_hmac_key(hmac_key, persistent_cache=self.cache_dir is not None)
        self.ttl_seconds = ttl_seconds
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.clock = clock
        self.wall_clock = wall_clock
        self.sleeper = sleeper
        self._last_call: dict[str, float] = {}
        self._throttle_locks = {service: threading.Lock() for service in ENDPOINTS}

    def search(self, service: str, query: str, *, limit: int = 10) -> APIResult:
        if service not in ENDPOINTS:
            raise ValidationError("Unsupported service")
        clean = _validate_query(query)
        _validate_approved_query(service, clean)
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValidationError("Limit must be 1–50")
        if self.transport is None:
            raise NetworkDisabled("R6 network egress disabled; offline transport required")
        host, path = ENDPOINTS[service]
        params = {"query": clean, "format": "json", "pageSize": str(limit)} if service == "europe_pmc" else (
            {"keywordSearch": clean, "resultsPerPage": str(limit)} if service == "nvd" else
            {"db": "pubmed", "term": clean, "retmode": "json", "retmax": str(limit), "tool": "EmergencyEvidencePilot"})
        # Only fixed, allow-listed HTTPS URLs. NCBI key, when present, is not returned in provenance.
        public_url = "https://" + host + path + "?" + urlencode(params)
        request_url = public_url
        headers: dict[str, str] = {"User-Agent": "EmergencyEvidencePilot/0.1 (research-only)", "Accept": "application/json"}
        if service == "pubmed" and os.getenv("NCBI_API_KEY"):
            # NCBI requires GET query credentials; block rather than risk proxy logs.
            raise ValidationError("NCBI API key use disabled pending redacted egress approval")
        if service == "nvd" and os.getenv("NVD_API_KEY"):
            headers["apiKey"] = os.environ["NVD_API_KEY"]
        safe = urlsplit(public_url)
        if safe.scheme != "https" or safe.hostname != host or safe.path != path:
            raise APIGatewayError("Endpoint not allow-listed")
        key = hmac.new(self._hmac_key,
                       (service + "\0" + clean + "\0" + str(limit)).encode("utf-8"),
                       hashlib.sha256).hexdigest()
        cached = self._cache_read(key)
        if cached is not None:
            raw, cached_at, raw_body_hash = cached
            records, total = _records(service, raw)
            return APIResult(service, records, total,
                             self._provenance(service, public_url, cached_at, True, key, raw,
                                              limit, raw_body_hash, "cache_hit"))
        for attempt in range(self.retries + 1):
            self._throttle(service)
            try:
                reply = self.transport(request_url, headers, self.timeout_seconds)
            except (TimeoutError, URLError, OSError, http.client.HTTPException) as exc:
                if attempt == self.retries:
                    raise APIGatewayError(f"Network transport failed after {attempt+1} attempt(s)") from None
                self._delay(attempt, None)
                continue
            reply = _validate_transport_reply(reply)
            if reply.status in RETRYABLE and attempt < self.retries:
                retry_header = next((v for k, v in reply.headers.items() if k.lower() == "retry-after"), None)
                self._delay(attempt, retry_header)
                continue
            raw = _validate_response(reply)
            records, total = _records(service, raw)
            raw_body_hash = hashlib.sha256(reply.body).hexdigest()
            timestamp = datetime.now(timezone.utc).isoformat()
            cache_status = self._cache_write(key, raw, timestamp, raw_body_hash)
            return APIResult(service, records, total,
                             self._provenance(service, public_url, timestamp, False, key,
                                              raw, limit, raw_body_hash, cache_status))
        raise APIGatewayError("Unexpected retry state")

    def _throttle(self, service: str) -> None:
        interval = MIN_INTERVAL_SECONDS[service]
        # Key-enabled NVD still uses conservative rate in this simple proof of concept.
        with self._throttle_locks[service]:
            now = self.clock()
            previous = self._last_call.get(service)
            if previous is not None and now - previous < interval:
                self.sleeper(interval - (now - previous))
            self._last_call[service] = self.clock()

    def _delay(self, attempt: int, retry_after: str | None) -> None:
        delay = min(2 ** attempt, 8)
        if retry_after is not None:
            try:
                n = float(retry_after)
                if math.isfinite(n) and n >= 0:
                    delay = min(n, 8)
            except (ValueError, TypeError):
                try:
                    when = parsedate_to_datetime(retry_after)
                    if when.tzinfo is not None:
                        wait = (when - datetime.now(timezone.utc)).total_seconds()
                        if math.isfinite(wait):
                            delay = min(max(0.0, wait), 8)
                except (ValueError, TypeError, OverflowError):
                    pass
        self.sleeper(delay)

    def _cache_path(self, key: str) -> Path:
        assert self.cache_dir is not None
        return self.cache_dir / (key + ".json")

    def _cache_read(self, key: str) -> tuple[dict, str, str] | None:
        if self.cache_dir is None:
            return None
        path = self._cache_path(key)
        try:
            # Only ever trust authenticated records. Never follow a symlink.
            if path.is_symlink():
                return None
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
            fd = os.open(path, flags)
            try:
                meta = os.fstat(fd)
                if (meta.st_size > MAX_CACHE_ENVELOPE_BYTES or
                        not _safe_posix_cache_metadata(meta, is_dir=False)):
                    return None
                blob = os.read(fd, MAX_CACHE_ENVELOPE_BYTES + 1)
            finally:
                os.close(fd)
            if len(blob) > MAX_CACHE_ENVELOPE_BYTES:
                return None
            obj = _safe_json_loads(blob)
            signature = obj.pop("hmac_sha256", None)
            if not (isinstance(signature, str) and re.fullmatch("[0-9a-f]{64}", signature)):
                return None
            expected = hmac.new(self._hmac_key, _canonical_bytes(obj), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                return None
            if obj.get("cache_key") != key:
                return None
            if not isinstance(obj.get("content"), dict) or not isinstance(obj.get("retrieved_at"), str):
                return None
            raw_hash = obj.get("raw_body_sha256")
            if not isinstance(raw_hash, str) or not re.fullmatch("[0-9a-f]{64}", raw_hash):
                return None
            fetched_unix = obj.get("fetched_unix")
            if type(fetched_unix) not in (int, float) or not math.isfinite(fetched_unix):
                return None
            now = self.wall_clock()
            if now < fetched_unix or now - fetched_unix > self.ttl_seconds:
                return None
            return obj["content"], obj["retrieved_at"], raw_hash
        except (OSError, ValueError, TypeError, KeyError, APIGatewayError, AttributeError):
            return None

    def _cache_write(self, key: str, data: dict, timestamp: str,
                     raw_body_hash: str) -> str:
        """Write authenticated cache, returning a bounded non-sensitive status.

        Skipping a too-large envelope is explicitly reported in provenance;
        unlike an HTTP response-size violation this is a safe cache miss.
        """
        if self.cache_dir is None:
            return "cache_disabled"
        if self.cache_dir.is_symlink():
            raise APIGatewayError("Cache directory cannot be a symbolic link")
        try:
            self.cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
            meta = self.cache_dir.stat(follow_symlinks=False)
            if not _safe_posix_cache_metadata(meta, is_dir=True):
                raise APIGatewayError("Cache directory has unsafe permissions")
        except OSError:
            raise APIGatewayError("Cache directory is unavailable") from None
        envelope = {"cache_key": key, "retrieved_at": timestamp,
                    "fetched_unix": self.wall_clock(), "raw_body_sha256": raw_body_hash,
                    "content": data}
        envelope["hmac_sha256"] = hmac.new(self._hmac_key, _canonical_bytes(envelope),
                                          hashlib.sha256).hexdigest()
        payload = _canonical_bytes(envelope)
        if len(payload) > MAX_CACHE_ENVELOPE_BYTES:
            return "skipped_envelope_size_limit"
        tmp = self.cache_dir / (key + "." + secrets.token_hex(12) + ".tmp")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        try:
            fd = os.open(tmp, flags, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self._cache_path(key))
            return "stored"
        except OSError:
            raise APIGatewayError("Safe cache write failed") from None
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def _provenance(service: str, url: str, timestamp: str, cache_hit: bool,
                    key: str, normalized: dict, limit: int, raw_body_hash: str,
                    cache_write_status: str = "cache_disabled") -> dict:
        return {"source": service, "endpoint": urlsplit(url)._replace(query="").geturl(),
                "query_fingerprint_hmac_sha256": key,
                "retrieved_utc": timestamp, "from_cache": cache_hit,
                "cache_write_status": cache_write_status,
                "client_version": CLIENT_VERSION, "http_status": 200,
                "raw_body_sha256": raw_body_hash,
                "normalized_content_sha256": hashlib.sha256(_canonical_bytes(normalized)).hexdigest(),
                "requested_limit": limit,
                "api_family": {"pubmed": "NCBI E-utilities ESearch", "europe_pmc": "Europe PMC REST",
                               "nvd": "NIST NVD CVE API 2.0"}[service],
                "content_license": None, "license_verified": False,
                "external_data_trust": "untrusted_not_safe_for_html_or_llm_instructions",
                "scope": "technical_reference_only_not_clinically_validated"}
