#!/usr/bin/env python3
"""Publish allowlisted scan metadata, never snippets, messages or secret values."""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def fingerprint(tool, path, rule, package="", version="", extra=""):
    value = json.dumps([tool, path, rule, package, version, extra], ensure_ascii=True)
    return hashlib.sha256(value.encode()).hexdigest()


def trivy_severity(item):
    severity = item["Severity"]
    if severity not in {"UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValueError("Invalid Trivy severity")
    return severity


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
                    "severity": trivy_severity(item),
                    "fingerprint": fingerprint(tool, path, rule, package, version),
                })
            for key, kind in [("Secrets", "secret"), ("Misconfigurations", "misconfiguration")]:
                for item in result.get(key, []):
                    rule = item.get("RuleID") or item.get("ID") or "unknown"
                    line = item.get("StartLine") or item.get("CauseMetadata", {}).get("StartLine", 0)
                    findings.append({
                        "tool": tool, "kind": kind, "rule": rule,
                        "file": path, "line": line,
                        "severity": trivy_severity(item),
                        "fingerprint": fingerprint(tool, path, rule, extra=str(line)),
                    })
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=["semgrep", "trivy"])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-target", action="append", default=[])
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        targets = data.get("paths", {}).get("scanned", []) if args.tool == "semgrep" else [r["Target"] for r in data.get("Results", [])]
        normalized = {p.removeprefix("/src/") for p in targets}
        if not set(args.require_target).issubset(normalized):
            raise ValueError("Required scan targets missing")
        findings = collect(args.tool, data)
        baseline_path = Path(__file__).resolve().parents[2] / "security" / "baseline.json"
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
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
    except (OSError, ValueError, KeyError, TypeError):
        report = {"schema_version": 1, "tool": args.tool, "status": "ERROR",
                  "reason": "Missing, malformed or incomplete scanner report", "findings": []}
    # The classifier never accepts filesystem paths from CLI input. Raw data is
    # read from stdin; metadata is emitted to stdout for runner-owned redirection.
    json.dump(report, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")
    print(f"{args.tool}: {report['status']}; {len(report['findings'])} findings", file=sys.stderr)
    if args.check:
        raise SystemExit(2 if report["status"] == "ERROR" else int(report["status"] == "FINDINGS"))


if __name__ == "__main__":
    main()
