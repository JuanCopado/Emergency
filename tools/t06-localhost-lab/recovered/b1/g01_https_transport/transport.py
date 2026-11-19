"""G-01 prototype: HTTPS transport with an ABSOLUTE deadline enforced by process kill.

Interface: HardenedHTTPSTransport.__call__(url, headers, timeout) -> emergency_apis.clients.HTTPReply,
i.e. the R6 `transport` callable contract. R6 is imported, never modified.

Deadline semantics
  * Clock: CLOCK_BOOTTIME when available (counts system suspend), else time.monotonic().
  * deadline_abs = call_start + min(timeout, max_call_seconds, operation budget remaining).
    It covers: concurrency-slot wait, process spawn, DNS, TCP, TLS, request, headers, body, last byte.
  * Authority = the parent: at deadline it SIGKILLs the worker's process group and reaps it.
    The kernel closes the worker's sockets; nothing is left in a thread (no thread abandoned in
    getaddrinfo/connect/handshake). The worker also checks the same deadline cooperatively.
  * Cancellation: close() (or an operation scope) makes in-flight calls kill their worker within
    ~POLL_SECONDS and refuse new calls.
  * Process start-up (~0.1 s) is inside the budget; budgets below ~0.5 s are not meaningful.
"""
from __future__ import annotations

import json
import math
import logging
import os
import selectors
import signal
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from types import MappingProxyType

from emergency_apis.clients import APIClient, APIGatewayError, HTTPReply
from . import _policy

_LOG = logging.getLogger("g01_https_transport")   # codes + durations only; never URL/query/headers/body
POLL_SECONDS = 0.05
SPAWN_MARGIN = 0.15
MIN_ATTEMPT_SECONDS = 0.5
_WORKER = str(Path(__file__).with_name("_worker.py"))


def _now() -> float:
    return time.clock_gettime(time.CLOCK_BOOTTIME) if hasattr(time, "CLOCK_BOOTTIME") else time.monotonic()


def _finite_number_in_range(value, minimum: float, maximum: float) -> bool:
    """Validate externally supplied numeric settings; bool is not a numeric setting."""
    return type(value) in (int, float) and minimum <= value <= maximum and math.isfinite(value)


def _integer_in_range(value, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


class G01TransportError(APIGatewayError):
    """Non-retryable by R6 (not OSError). Message = fixed code only."""
    def __init__(self, code: str):
        super().__init__(f"G01 transport failure: {code}")
        self.code = code


class G01NetworkError(OSError):
    """Retryable by R6 (OSError class)."""
    def __init__(self, code: str):
        super().__init__(f"G01 transport failure: {code}")
        self.code = code


class G01Timeout(TimeoutError):
    def __init__(self):
        super().__init__("G01 transport failure: timeout")
        self.code = "timeout"


def _raise(code: str):
    if code == "timeout":
        raise G01Timeout() from None
    if code not in _policy.ERROR_CODES:
        code = "protocol_error"
    if _policy.ERROR_CODES[code]:
        raise G01NetworkError(code) from None
    raise G01TransportError(code) from None


# ---------------- operation budget (global across attempts + sleeps) ----------------
_tls = threading.local()


class OperationBudget:
    """Total operation budget in seconds. Same domain as G01Gateway.total_budget_seconds.

    Accepted: exactly `int` or `float` (not bool, not subclasses, not Decimal/Fraction/numpy),
    finite, 1.0 <= value <= 60.0. Anything else raises ValueError("invalid operation budget")
    with a fixed message that never echoes the input (G01-B1-R2).
    """

    def __init__(self, total_seconds: float):
        if not _finite_number_in_range(total_seconds, 1.0, 60.0):
            raise ValueError("invalid operation budget")
        self.deadline = _now() + total_seconds

    def remaining(self) -> float:
        return self.deadline - _now()


@contextmanager
def operation_scope(budget: OperationBudget):
    # Entry check: only a genuine OperationBudget with a finite float deadline may become the active
    # scope (guards direct use, subclasses/duck-typed fakes and a deadline mutated after construction).
    if (type(budget) is not OperationBudget or type(budget.deadline) is not float
            or not math.isfinite(budget.deadline)):
        raise ValueError("invalid operation budget")
    prev = getattr(_tls, "budget", None)
    _tls.budget = budget
    try:
        yield budget
    finally:
        _tls.budget = prev


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.spawned = self.unreaped = self.killed = 0
        self.live = self.peak_live = 0


class HardenedHTTPSTransport:
    def __init__(self, *, max_concurrency: int = 4, max_call_seconds: float = 15.0,
                 _worker_script: str | None = None, _worker_env: dict | None = None):
        if not (_integer_in_range(max_concurrency, 1, 16)
                and _finite_number_in_range(max_call_seconds, 0.5, 30.0)):
            raise ValueError("invalid transport configuration")
        self.max_call_seconds = max_call_seconds
        self._slots = threading.BoundedSemaphore(max_concurrency)
        self._closed = threading.Event()
        self._live: set[subprocess.Popen] = set()
        self._live_lock = threading.Lock()
        self.stats = Stats()
        # underscore params: test profiles only. Production default is the fixed worker, empty env.
        self._worker = _worker_script or _WORKER
        self._env = dict(_worker_env or {})

    # ---- R6 transport contract ----
    def __call__(self, url, headers, timeout) -> HTTPReply:
        start = _now()
        try:
            checked_timeout = _policy.validate_timeout(timeout)
            host, target, clean = _policy.parse_request(url, headers)
        except _policy.PolicyError as e:
            _raise(e.code)
        if self._closed.is_set():
            _raise("closed")
        limit = min(checked_timeout, self.max_call_seconds)
        budget = getattr(_tls, "budget", None)
        if budget is not None:
            limit = min(limit, budget.remaining())
            if limit < MIN_ATTEMPT_SECONDS:
                _raise("budget_exhausted")
        deadline = start + limit
        status, hdrs, body, code = self._run(host, target, clean, deadline)
        elapsed = _now() - start
        _LOG.info("g01 call result=%s elapsed=%.3f limit=%.3f", code or "ok", elapsed, limit)
        if code:
            _raise(code)
        return HTTPReply(status, body, MappingProxyType(hdrs))

    def close(self) -> None:
        self._closed.set()

    # ---- internals ----
    def _acquire_slot(self, deadline: float) -> bool:
        while True:
            if self._closed.is_set():
                return False
            r = deadline - _now()
            if r <= 0:
                return False
            if self._slots.acquire(timeout=min(r, POLL_SECONDS)):
                return True

    def _run(self, host, target, clean, deadline):
        if not self._acquire_slot(deadline):
            return None, None, None, ("closed" if self._closed.is_set() else "saturated")
        proc = None
        try:
            remaining = deadline - _now() - SPAWN_MARGIN
            if remaining <= 0.05:
                return None, None, None, "timeout"
            spec = json.dumps({"host": host, "target": target, "headers": clean, "remaining": remaining}).encode("ascii")
            env = {"PATH": "/usr/bin:/bin", **self._env}
            proc = subprocess.Popen([sys.executable, "-I", self._worker], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env,
                                    close_fds=True, start_new_session=True)
            with self.stats.lock:
                self.stats.spawned += 1
                self.stats.live += 1
                self.stats.peak_live = max(self.stats.peak_live, self.stats.live)
            with self._live_lock:
                self._live.add(proc)
            try:
                proc.stdin.write(spec)
                proc.stdin.close()
            except OSError:
                pass
            return self._collect(proc, deadline)
        except OSError:
            return None, None, None, "worker_failed"
        finally:
            if proc is not None:
                self._reap(proc)
            self._slots.release()

    def _collect(self, proc, deadline):
        fd = proc.stdout.fileno()
        os.set_blocking(fd, False)
        sel = selectors.DefaultSelector()
        sel.register(fd, selectors.EVENT_READ)
        buf = bytearray()
        cap = _policy.MAX_BODY_BYTES + _policy.MAX_FRAME_HEAD_BYTES
        try:
            while True:
                if self._closed.is_set():
                    return None, None, None, "closed"
                r = deadline - _now()
                if r <= 0:
                    return None, None, None, "timeout"
                if not sel.select(timeout=min(r, POLL_SECONDS)):
                    continue
                try:
                    chunk = os.read(fd, 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    break
                buf += chunk
                if len(buf) > cap:
                    return None, None, None, "response_too_large"
        finally:
            sel.close()
        return self._parse_frame(bytes(buf))

    @staticmethod
    def _parse_frame(buf: bytes):
        nl = buf.find(b"\n")
        if nl < 0 or nl > _policy.MAX_FRAME_HEAD_BYTES:
            return None, None, None, "worker_failed"
        try:
            head = json.loads(buf[:nl].decode("ascii"))
        except (ValueError, UnicodeError):
            return None, None, None, "worker_failed"
        if not isinstance(head, dict):
            return None, None, None, "worker_failed"
        if head.get("ok") is False:
            c = head.get("code")
            return None, None, None, c if isinstance(c, str) and c in _policy.ERROR_CODES else "worker_failed"
        body = buf[nl + 1:]
        st, hd, bl = head.get("status"), head.get("headers"), head.get("body_len")
        if (head.get("ok") is not True or type(st) is not int or not 200 <= st <= 599 or type(bl) is not int
                or bl != len(body) or bl > _policy.MAX_BODY_BYTES or not isinstance(hd, dict)
                or len(hd) > _policy.MAX_HEADER_COUNT
                or any(not isinstance(k, str) or not isinstance(v, str) for k, v in hd.items())
                or sum(len(k) + len(v) for k, v in hd.items()) > _policy.MAX_HEADER_BYTES
                or (st != 200 and bl != 0)):
            return None, None, None, "worker_failed"
        return st, hd, body, None

    def _reap(self, proc):
        try:
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)   # pgid == pid (start_new_session)
                except ProcessLookupError:
                    pass
                with self.stats.lock:
                    self.stats.killed += 1
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                with self.stats.lock:
                    self.stats.unreaped += 1
                _LOG.error("g01 worker not reaped")
        finally:
            for f in (proc.stdout, proc.stdin):
                try:
                    if f:
                        f.close()
                except OSError:
                    pass
            with self._live_lock:
                self._live.discard(proc)
            with self.stats.lock:
                self.stats.live -= 1


class G01Gateway:
    """R6 APIClient + global operation budget. Budget covers attempts, throttle sleeps,
    Retry-After sleeps and queueing. R6 code is used unmodified via its public arguments."""

    def __init__(self, *, total_budget_seconds: float = 20.0, attempt_timeout_seconds: float = 6.0,
                 retries: int = 2, max_concurrency: int = 4, transport: HardenedHTTPSTransport | None = None,
                 **client_kwargs):
        if not _finite_number_in_range(total_budget_seconds, 1.0, 60.0):
            raise ValueError("invalid budget")
        if not (_finite_number_in_range(attempt_timeout_seconds, 1.0, 30.0)
                and _integer_in_range(max_concurrency, 1, 16)
                and _integer_in_range(retries, 0, 3)):
            raise ValueError("invalid gateway configuration")
        self.total_budget = total_budget_seconds
        self.transport = transport or HardenedHTTPSTransport(max_concurrency=max_concurrency,
                                                             max_call_seconds=attempt_timeout_seconds)
        self._cancel = threading.Event()
        self._service_locks: dict[str, threading.Lock] = {}
        self._guard = threading.Lock()
        self.client = APIClient(transport=self.transport, timeout_seconds=attempt_timeout_seconds,
                                retries=retries, sleeper=self._sleep, **client_kwargs)

    def _sleep(self, seconds: float) -> None:
        b = getattr(_tls, "budget", None)
        if b is None or seconds >= b.remaining() - MIN_ATTEMPT_SECONDS:
            _raise("budget_exhausted")        # never sleep into a doomed attempt
        if self._cancel.wait(seconds):
            _raise("closed")

    def search(self, service: str, query: str, *, limit: int = 10):
        budget = OperationBudget(self.total_budget)
        # Serialise per service so R6's internal throttle lock is never contended outside our budget.
        with self._guard:
            lock = self._service_locks.setdefault(service, threading.Lock())
        if not lock.acquire(timeout=max(0.0, budget.remaining() - MIN_ATTEMPT_SECONDS)):
            _raise("saturated")
        try:
            with operation_scope(budget):
                return self.client.search(service, query, limit=limit)
        finally:
            lock.release()

    def close(self) -> None:
        self._cancel.set()
        self.transport.close()
