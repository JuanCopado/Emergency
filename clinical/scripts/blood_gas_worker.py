"""Contain PDF and OCR parsing in a bounded Windows process tree."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from cli_paths import input_file

MEMORY = 768 * 1024 * 1024
OUTPUT = 40 * 1024 * 1024

def restrict_worker():
    if os.name != "nt":
        raise RuntimeError("Resource containment requires Windows Job Objects")

    class Basic(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("minimum", ctypes.c_size_t),
                    ("maximum", ctypes.c_size_t), ("processes", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                    ("scheduling", wintypes.DWORD)]

    class Counters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in (
            "read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class Extended(ctypes.Structure):
        _fields_ = [("basic", Basic), ("io", Counters),
                    ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                    ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    handle = kernel.CreateJobObjectW(None, None)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    limits = Extended()
    # Aggregate memory, kill descendants on worker exit, aggregate CPU time.
    limits.basic.flags = 0x200 | 0x2000 | 0x4
    limits.basic.job_time = 60 * 10_000_000
    limits.job_memory = MEMORY
    if not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.AssignProcessToJobObject(handle, kernel.GetCurrentProcess()):
        raise ctypes.WinError(ctypes.get_last_error())
    return handle

def safe_extract(data, regions=None):
    limit = int(os.getenv("BG_MAX_BYTES", 8 * 1024 * 1024))
    if not data or len(data) > limit:
        raise ValueError("Input size limit")
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory, "source.bin")
        options = Path(directory, "regions.json")
        output = Path(directory, "output.json")
        with source.open("xb") as stream:
            stream.write(data)
        with options.open("x", encoding="utf8") as stream:
            json.dump(regions, stream, allow_nan=False)
        # Only the parent-generated private directory grants child read access.
        environment = dict(os.environ, EMERGENCY_CLI_INPUT_ROOT=directory)
        with output.open("wb") as stream:
            process = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--worker", str(source), str(options)],
                stdout=stream, stderr=subprocess.DEVNULL, env=environment)
            try:
                code = process.wait(timeout=120)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                raise ValueError("Extraction time limit")
        if code or output.stat().st_size > OUTPUT:
            raise ValueError("Extraction failed or resource limit exceeded")
        return json.loads(output.read_text(encoding="utf8"))

if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "--worker":
        raise SystemExit(2)
    source = input_file(sys.argv[2])
    options = input_file(sys.argv[3])
    job_handle = restrict_worker()
    from blood_gas_review import extract, LIMIT
    with source.open("rb") as stream:
        data = stream.read(LIMIT + 1)
    regions = json.loads(options.read_text(encoding="utf8"))
    payload = json.dumps(extract(data, regions), ensure_ascii=True, allow_nan=False)
    if len(payload) > OUTPUT:
        raise SystemExit(3)
    sys.stdout.write(payload)
