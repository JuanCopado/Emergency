"""Pure policy constants/validators shared by parent and worker. No I/O, no R6 imports."""
import math
import re
from collections.abc import Mapping
from types import MappingProxyType
from urllib.parse import parse_qsl, urlsplit

# Exactly three hosts, constant paths. Port is always 443 (not configurable here).
ALLOWED_ENDPOINTS = MappingProxyType({
    "eutils.ncbi.nlm.nih.gov": "/entrez/eutils/esearch.fcgi",
    "www.ebi.ac.uk": "/europepmc/webservices/rest/search",
    "services.nvd.nist.gov": "/rest/json/cves/2.0",
})

# Explicitly bounded public query parameters for each provider; no API credentials.
ALLOWED_QUERY_PARAMS = MappingProxyType({
    "eutils.ncbi.nlm.nih.gov": frozenset({"db", "term", "retmode", "retmax", "tool"}),
    "www.ebi.ac.uk": frozenset({"query", "format", "pageSize"}),
    "services.nvd.nist.gov": frozenset({"keywordSearch", "resultsPerPage"}),
})
MAX_TIMEOUT_SECONDS = 30.0
MAX_BODY_BYTES = 2_000_000          # same cap as R6 MAX_RESPONSE_BYTES
MAX_HEADER_COUNT = 64
MAX_HEADER_BYTES = 16_384           # sum of len(name)+len(value) over all headers
MAX_QUERY_CHARS = 1024
MAX_FRAME_HEAD_BYTES = 40_000       # worker->parent JSON head line
ALLOWED_REQUEST_HEADERS = frozenset({"user-agent", "accept"})
CREDENTIAL_HEADERS = frozenset({"apikey", "authorization", "x-api-key"})
SENSITIVE_SINGLETONS = frozenset({"content-length", "transfer-encoding", "content-encoding",
                                  "retry-after", "location", "content-type"})

# code -> retryable by the R6 retry loop (network class) or not (fail closed)
ERROR_CODES = MappingProxyType({
    "timeout": True, "dns_failure": True, "connect_failed": True, "connection_reset": True,
    "truncated_body": True,
    "dns_non_global": False, "tls_verify_failed": False, "tls_error": False,
    "redirect_blocked": False, "response_too_large": False, "headers_too_large": False,
    "content_encoding_unsupported": False, "ambiguous_framing": False, "protocol_error": False,
    "informational_response": False, "url_not_allowed": False, "credential_not_approved": False,
    "saturated": False, "closed": False, "budget_exhausted": False, "worker_failed": False,
    "bad_request_headers": False, "invalid_timeout": False,
})

_QUERY_RE = re.compile(r"[A-Za-z0-9%._~+=&-]*", re.ASCII)
HEADER_NAME_RE = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]{1,128}", re.ASCII)
HEADER_VALUE_RE = re.compile(r"[\t\x20-\x7e]{0,2048}", re.ASCII)
_HDR_VALUE_RE = re.compile(r"[\x20-\x7e]{1,200}", re.ASCII)


class PolicyError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def validate_timeout(value):
    """Keep non-finite/invalid timeouts away from DNS, slot allocation and deadlines."""
    if type(value) not in (int, float) or not 0 < value <= MAX_TIMEOUT_SECONDS:
        raise PolicyError("invalid_timeout")
    try:
        if not math.isfinite(value):
            raise PolicyError("invalid_timeout")
        return float(value)
    except (OverflowError, ValueError, TypeError):
        raise PolicyError("invalid_timeout") from None


def _validate_query(query: str, host: str) -> None:
    """Require canonical parameter names and ASCII values, never decoded credentials."""
    if not query or len(query) > MAX_QUERY_CHARS or not _QUERY_RE.fullmatch(query):
        raise PolicyError("url_not_allowed")
    if re.search(r"%(?![0-9A-Fa-f]{2})", query):
        raise PolicyError("url_not_allowed")
    # %25 encodes a literal %, enabling double-decoding differences at proxies.
    if re.search(r"%25", query, flags=re.IGNORECASE):
        raise PolicyError("url_not_allowed")
    raw_pairs = query.split("&")
    if any("=" not in pair or pair == "" for pair in raw_pairs):
        raise PolicyError("url_not_allowed")
    try:
        pairs = parse_qsl(query, keep_blank_values=True, strict_parsing=True,
                          encoding="utf-8", errors="strict", max_num_fields=16)
    except (ValueError, UnicodeError):
        raise PolicyError("url_not_allowed") from None
    if len(pairs) != len(raw_pairs):
        raise PolicyError("url_not_allowed")
    if any(name.lower() in {"api_key", "apikey", "key", "token", "access_token"} for name, _ in pairs):
        raise PolicyError("credential_not_approved")
    seen = set()
    for (decoded_name, decoded_value), raw_pair in zip(pairs, raw_pairs):
        raw_name = raw_pair.split("=", 1)[0]
        if (raw_name != decoded_name or decoded_name not in ALLOWED_QUERY_PARAMS[host]
                or decoded_name in seen):
            raise PolicyError("url_not_allowed")
        seen.add(decoded_name)
        if not decoded_value.isascii() or any(not 32 <= ord(ch) < 127 for ch in decoded_value):
            raise PolicyError("url_not_allowed")


def parse_request(url, headers):
    """Return (host, target, headers). All exceptions have a fixed safe code."""
    if not isinstance(url, str) or len(url) > 2048 or not url.isascii():
        raise PolicyError("url_not_allowed")
    try:
        s = urlsplit(url)
        host_attr = s.hostname
        port = s.port
    except ValueError:
        raise PolicyError("url_not_allowed") from None
    if (s.scheme != "https" or port is not None or s.username is not None or s.password is not None
            or s.fragment or host_attr is None or s.netloc != host_attr
            or ALLOWED_ENDPOINTS.get(host_attr) != s.path):
        raise PolicyError("url_not_allowed")
    _validate_query(s.query, host_attr)
    if not isinstance(headers, Mapping):
        raise PolicyError("bad_request_headers")
    clean = {}
    try:
        for k, v in headers.items():
            if type(k) is not str or type(v) is not str:
                raise PolicyError("bad_request_headers")
            lk = k.lower()
            if lk in CREDENTIAL_HEADERS:
                raise PolicyError("credential_not_approved")
            if lk not in ALLOWED_REQUEST_HEADERS or lk in clean or not _HDR_VALUE_RE.fullmatch(v):
                raise PolicyError("bad_request_headers")
            clean[lk] = v
    except PolicyError:
        raise
    except (AttributeError, TypeError, ValueError, RuntimeError, KeyError, UnicodeError):
        raise PolicyError("bad_request_headers") from None
    target = s.path + "?" + s.query
    return host_attr, target, clean
