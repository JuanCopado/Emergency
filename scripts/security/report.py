#!/usr/bin/env python3
"""Publish allowlisted scan metadata, never snippets, messages or secret values."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


def fingerprint(tool, path, rule, package="", version="", extra=""):
    value = json.dumps([tool, path, rule, package, version, extra], ensure_ascii=True)
    return hashlib.sha256(value.encode()).hexdigest()


def collect(tool, data):
    findings = []
    if tool == "semgrep":
        if data.get("errors"):
            raise ValueError("Semgrep reported scan errors; inspect runner-local diagnostics")
        for item in data["results"]:
            extra = item.get("extra", {})
            rule = item["check_id"]
            path = item["path"].removeprefix("/src/")
            # The scanner's fingerprint does not contain source text.
            identity = extra.get("fingerprint") or str(item["start"]["line"])
            findings.append({
                "tool": tool, "rule": rule, "file": path,
                "line": item["start"]["line"],
                "severity": extra.get("severity", "UNKNOWN"),
                "fingerprint": fingerprint(tool, path, rule, extra=identity),
            })
    else:
        if data.get("SchemaVersion") != 2:
            raise ValueError("Unsupported Trivy report schema")
        for result in data.get("Results", []):
            path = result["Target"].removeprefix("/src/")
            for item in result.get("Vulnerabilities", []):
                rule, package, version = item["VulnerabilityID"], item["PkgName"], item["InstalledVersion"]
                findings.append({
                    "tool": tool, "kind": "vulnerability", "rule": rule,
                    "file": path, "package": package, "installed_version": version,
                    "fixed_version": item.get("FixedVersion", ""),
                    "severity": item.get("Severity", "UNKNOWN"),
                    "fingerprint": fingerprint(tool, path, rule, package, version),
                })
            for key, kind in [("Secrets", "secret"), ("Misconfigurations", "misconfiguration")]:
                for item in result.get(key, []):
                    rule = item.get("RuleID") or item.get("ID") or "unknown"
                    line = item.get("StartLine") or item.get("CauseMetadata", {}).get("StartLine", 0)
                    findings.append({
                        "tool": tool, "kind": kind, "rule": rule,
                        "file": path, "line": line,
                        "severity": item.get("Severity", "UNKNOWN"),
                        "fingerprint": fingerprint(tool, path, rule, extra=str(line)),
                    })
    return findings



# Input/output filenames are fixed by the tool, never supplied via CLI.
# RUNNER_TEMP is a GitHub Actions runner-controlled directory; local test runs
# must explicitly provide an isolated absolute RUNNER_TEMP.
MAX_RAW_REPORT_BYTES = 32 * 1024 * 1024


def _report_paths(tool):
    runner_temp = os.environ.get("RUNNER_TEMP", "")
    if not runner_temp or not os.path.isabs(runner_temp):
        raise ValueError("RUNNER_TEMP must identify an absolute runner-owned directory")
    root = Path(runner_temp)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("RUNNER_TEMP must be a real directory")
    report_dir = root / "security"
    if report_dir.is_symlink() or (report_dir.exists() and not report_dir.is_dir()):
        raise ValueError("Invalid report directory")
    report_dir.mkdir(mode=0o700, exist_ok=True)
    os.chmod(report_dir, 0o700)
    raw = report_dir / f"{tool}.raw.json"
    output = report_dir / f"{tool}.summary.json"
    if raw.is_symlink() or output.is_symlink():
        raise ValueError("Symlinked report files are not permitted")
    return raw, output


def _load_scan(path):
    # O_NOFOLLOW protects against a symlink swap between validation and open.
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, os.O_RDONLY | nofollow)
    with os.fdopen(fd, "rb") as stream:
        content = stream.read(MAX_RAW_REPORT_BYTES + 1)
    if len(content) > MAX_RAW_REPORT_BYTES:
        raise ValueError("Scanner report exceeds size limit")
    return json.loads(content)


def _atomic_write(path, data):
    if path.is_symlink():
        raise ValueError("Refusing to replace symlinked report")
    content = json.dumps(data, indent=2, ensure_ascii=True) + "\n"
    fd, staging = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(content)
        os.replace(staging, path)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=["semgrep", "trivy"])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-target", action="append", default=[])
    args = parser.parse_args()

    try:
        raw, output = _report_paths(args.tool)
    except (OSError, ValueError):
        print(f"{args.tool}: ERROR; invalid runner report directory")
        raise SystemExit(2)

    try:
        data = _load_scan(raw)
        targets = data.get("paths", {}).get("scanned", []) if args.tool == "semgrep" else [r["Target"] for r in data.get("Results", [])]
        normalized = {p.removeprefix("/src/") for p in targets}
        if not set(args.require_target).issubset(normalized):
            raise ValueError("Required scan targets missing")
        findings = collect(args.tool, data)
        # The baseline location is anchored to this checkout, not a CLI path.
        baseline_file = Path(__file__).resolve().parents[2] / "security" / "baseline.json"
        baseline = json.loads(baseline_file.read_text()) if baseline_file.exists() else {"findings": []}
        known = {item["fingerprint"] for item in baseline["findings"]}
        for finding in findings:
            finding["origin"] = "PREEXISTING" if finding["fingerprint"] in known else "NEW_OR_CHANGED"
            finding["owner"] = "UNASSIGNED"
            finding["priority"] = "P1" if finding.get("kind") == "secret" or finding["severity"] in {"HIGH", "CRITICAL", "ERROR"} else "P2"
            finding["next_action"] = "Review trust boundary and remediate; do not suppress without a dated decision"
        blockers = [f for f in findings if args.tool == "semgrep" or f.get("kind") == "secret"
                    or f["severity"] in {"HIGH", "CRITICAL"}]
        report = {"schema_version": 1, "tool": args.tool,
                  "status": "FINDINGS" if blockers else "PASS",
                  "scanned_targets": len(targets),
                  "blocking_findings": len(blockers), "findings": findings}
    except (OSError, ValueError, KeyError, TypeError, RecursionError, UnicodeError):
        report = {"schema_version": 1, "tool": args.tool, "status": "ERROR",
                  "reason": "Missing, malformed or incomplete scanner report", "findings": []}

    try:
        _atomic_write(output, report)
    except (OSError, ValueError):
        print(f"{args.tool}: ERROR; unable to write safe summary")
        raise SystemExit(2)

    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a") as stream:
            stream.write(f"### {args.tool}\n\nStatus: **{report['status']}**. "
                         f"Findings: {len(report['findings'])}. "
                         "See the metadata-only artifact. Clinical status is unchanged.\n\n")
    print(f"{args.tool}: {report['status']}; {len(report['findings'])} findings")
    if args.check:
        raise SystemExit(2 if report["status"] == "ERROR" else int(report["status"] == "FINDINGS"))


if __name__ == "__main__":
    main()
