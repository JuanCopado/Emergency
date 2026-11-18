"""Filesystem capability for operator CLI arguments, never HTTP payloads.

The trusted launcher selects EMERGENCY_CLI_ROOT (default: current directory).
A caller controlling argv cannot widen that root. External datasets remain
supported by choosing their workspace in the launcher environment. This is
an argv boundary, not a sandbox against an attacker controlling environment,
working directory, filesystem races, hard-link aliases, or arbitrary shell execution.
EMERGENCY_CLI_INPUT_ROOT and EMERGENCY_CLI_OUTPUT_ROOT can grant separate
read/write trees; each falls back to EMERGENCY_CLI_ROOT or cwd.
"""
import argparse
import os
from pathlib import Path


def _bounded_path(value, access):
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw or any(ord(c) < 32 for c in raw):
        raise argparse.ArgumentTypeError("invalid CLI path")
    # Windows alternate streams/device namespaces must not bypass file checks.
    if raw.startswith(("\\\\?\\", "\\\\.\\")):
        raise argparse.ArgumentTypeError("device paths are not permitted")
    root = os.environ.get(f"EMERGENCY_CLI_{access}_ROOT",
                          os.environ.get("EMERGENCY_CLI_ROOT", os.getcwd()))
    base = Path(root).resolve(strict=True)
    if not base.is_dir():
        raise argparse.ArgumentTypeError("CLI root must be an existing directory")
    candidate = Path(raw)
    if candidate.drive and not candidate.root:
        raise argparse.ArgumentTypeError("drive-relative paths are not permitted")
    parts = [part for part in candidate.parts if part != candidate.anchor]
    if any(":" in part for part in parts):
        raise argparse.ArgumentTypeError("alternate file streams are not permitted")
    devices = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$", "CLOCK$", "COM0", "LPT0"}
    devices.update(f"{prefix}{number}" for prefix in ("COM", "LPT")
                   for number in (*range(1, 10), "¹", "²", "³"))
    if any(part.split(".", 1)[0].rstrip(" ").upper() in devices
           or (part not in (".", "..") and part.rstrip(" .") != part)
           for part in parts):
        raise argparse.ArgumentTypeError("reserved or ambiguous filename")
    target = (base / candidate).resolve()
    if not target.is_relative_to(base):
        raise argparse.ArgumentTypeError("CLI path escapes the launcher workspace")
    return target


def input_file(value):
    target = _bounded_path(value, "INPUT")
    if not target.is_file():
        raise argparse.ArgumentTypeError("CLI input must be a regular file")
    return target


def input_directory(value):
    target = _bounded_path(value, "INPUT")
    if not target.is_dir():
        raise argparse.ArgumentTypeError("CLI input must be a directory")
    return target


def output_file(value):
    target = _bounded_path(value, "OUTPUT")
    if target.exists() and not target.is_file():
        raise argparse.ArgumentTypeError("CLI output must be a regular file")
    return target


def output_directory(value):
    target = _bounded_path(value, "OUTPUT")
    if target.exists() and not target.is_dir():
        raise argparse.ArgumentTypeError("CLI output must be a directory")
    return target
