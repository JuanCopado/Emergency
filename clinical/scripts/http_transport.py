"""Bounded transport for the local API; not authentication or a production gateway."""
import io
import logging
import math
import ssl
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class RequestRejection(ValueError):
    def __init__(self, status, public_message):
        super().__init__(public_message)
        self.status = status


def json_request_size(headers, maximum):
    """Reject ambiguous framing and browser-simple bodies before reading any bytes."""
    if headers.get_all("Transfer-Encoding"):
        raise RequestRejection(HTTPStatus.BAD_REQUEST, "transfer encoding is not supported")
    lengths = headers.get_all("Content-Length", [])
    if not lengths:
        raise RequestRejection(HTTPStatus.LENGTH_REQUIRED, "content length is required")
    if len(lengths) != 1:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, "ambiguous content length")
    length = lengths[0].strip(" \t")
    if not length.isascii() or not length.isdecimal() or len(length) > 10:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, "invalid content length")
    size = int(length)
    if size == 0:
        raise RequestRejection(HTTPStatus.BAD_REQUEST, "empty request body")
    if size > maximum:
        raise RequestRejection(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "request body is too large")
    types = headers.get_all("Content-Type", [])
    if len(types) != 1 or types[0].partition(";")[0].strip().lower() != "application/json":
        raise RequestRejection(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "application/json is required")
    if headers.get("Content-Encoding", "identity").strip().lower() != "identity":
        raise RequestRejection(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "content encoding is not supported")
    if headers.get("Sec-Fetch-Site", "").strip().lower() == "cross-site":
        raise RequestRejection(HTTPStatus.FORBIDDEN, "cross-site requests are not permitted")
    return size


class _DeadlineReader(io.RawIOBase):
    def __init__(self, connection, deadline):
        super().__init__()
        self.connection = connection
        self.deadline = deadline

    def readable(self):
        return True

    def readinto(self, buffer):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("request read deadline exceeded")
        self.connection.settimeout(remaining)
        return self.connection.recv_into(buffer)


class DeadlineRequestHandler(BaseHTTPRequestHandler):
    timeout = 15.0

    def setup(self):
        super().setup()
        # Recompute the remaining budget on EVERY recv, including reads inside
        # BufferedReader.readline/read. A trickle must not reset an idle timeout.
        self.rfile.close()
        self.timeout = getattr(self.server, "request_timeout", self.timeout)
        self.rfile = io.BufferedReader(
            _DeadlineReader(self.connection, time.monotonic() + self.timeout)
        )


class BoundedHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, handler, *, tls_context=None,
                 request_timeout=15.0, max_workers=16):
        if not math.isfinite(request_timeout) or not 0 < request_timeout <= 60:
            raise ValueError("request_timeout must be finite and in (0, 60]")
        if isinstance(max_workers, bool) or not isinstance(max_workers, int) or not 1 <= max_workers <= 128:
            raise ValueError("max_workers must be an integer in [1, 128]")
        self.tls_context = tls_context
        self.request_timeout = request_timeout
        self._slots = threading.BoundedSemaphore(max_workers)
        super().__init__(address, handler)

    def get_request(self):
        request, address = super().get_request()
        request.settimeout(self.request_timeout)
        return request, address

    def process_request(self, request, client_address):
        if not self._slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            if self.tls_context is not None:
                # Never wrap the listening socket: a peer withholding its TLS
                # handshake must not stall accept() for every other client.
                request = self.tls_context.wrap_socket(
                    request, server_side=True, do_handshake_on_connect=False
                )
                request.settimeout(self.request_timeout)
                request.do_handshake()
            self.finish_request(request, client_address)
        except (TimeoutError, ConnectionError, ssl.SSLError):
            pass  # Expected peer/transport failure; never emit submitted data.
        except Exception:
            self.handle_error(request, client_address)
        finally:
            try:
                self.shutdown_request(request)
            finally:
                self._slots.release()

    def handle_error(self, request, client_address):
        logging.getLogger(__name__).warning("HTTP request failed; connection closed")
