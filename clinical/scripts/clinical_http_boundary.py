"""Private loopback boundary for the existing clinical API.

The credential authenticates the local proxy process, not a clinician identity.
It is never returned by an endpoint or embedded in browser code.
"""
import hmac
import re
import secrets
from http import HTTPStatus

from http_transport import RequestRejection

TOKEN_HEADER = "X-Emergency-Local-Token"
LOOPBACK_PEERS = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}


def configure_local_server(server, *, ui_port=None, session_token=None):
    if server.server_address[0] not in LOOPBACK_PEERS:
        raise ValueError("The clinical API requires a loopback bind")
    if ui_port is not None and (type(ui_port) is not int or not 1 <= ui_port <= 65535):
        raise ValueError("UI port must be an integer in [1, 65535]")
    token = secrets.token_hex(32) if session_token is None else session_token
    if not isinstance(token, str) or re.fullmatch(r"[a-f0-9]{64}", token) is None:
        raise ValueError("The local API requires a 256-bit hexadecimal session credential")
    scheme = "https" if getattr(server, "tls_context", None) else "http"
    server.clinical_hosts = {f"127.0.0.1:{server.server_port}", f"localhost:{server.server_port}"}
    server.clinical_origins = {f"{scheme}://{host}" for host in server.clinical_hosts}
    if ui_port is not None:
        server.clinical_origins.update(f"http://{host}:{ui_port}" for host in ("127.0.0.1", "localhost"))
    server.clinical_session_token = token


def require_local_request(handler, *, credential=True):
    """Fail closed on unconfigured handlers, duplicate metadata and foreign origins."""
    server = handler.server
    hosts = handler.headers.get_all("Host", [])
    origins = handler.headers.get_all("Origin", [])
    sites = handler.headers.get_all("Sec-Fetch-Site", [])
    allowed_hosts = getattr(server, "clinical_hosts", set())
    allowed_origins = getattr(server, "clinical_origins", set())
    if (handler.client_address[0] not in LOOPBACK_PEERS or len(hosts) != 1
            or hosts[0] not in allowed_hosts or len(origins) > 1
            or (origins and origins[0] not in allowed_origins)
            or (credential and not origins) or len(sites) > 1
            or (sites and sites[0].strip().lower() not in {"same-origin", "same-site", "none"})):
        raise RequestRejection(HTTPStatus.FORBIDDEN, "local request origin is not permitted")
    if not credential:
        return
    tokens = handler.headers.get_all(TOKEN_HEADER, [])
    expected = getattr(server, "clinical_session_token", None)
    if (len(tokens) != 1 or not isinstance(expected, str) or not tokens[0].isascii()
            or not hmac.compare_digest(tokens[0], expected)):
        raise RequestRejection(HTTPStatus.UNAUTHORIZED, "local session credential required")
