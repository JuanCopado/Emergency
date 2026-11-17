# Initial security analysis — 16/11/2026

Base commit: `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`. Infrastructure only; clinical status remains `CLINICALLY_PENDING`.

## Observed local results

- actionlint 1.7.12: PASS for the new workflow (shellcheck disabled because not installed).
- YAML: parsed by actionlint and PyYAML BaseLoader.
- Semgrep 1.185.0: 12/12 rule tests PASS; full scan PASS, zero findings under those rules.
- Metadata/privacy and failure-propagation tests: 4/4 PASS.
- Trivy 0.76.2: completed; gate FAIL with 50 advisory occurrences (49 unique IDs): 3 CRITICAL, 16 HIGH, 26 MEDIUM, 5 LOW. No secret or misconfiguration findings in this scan.
- Three dependency targets verified: app/package-lock.json, clinical/requirements.txt and clinical/requirements-test.txt.
- All initial vulnerable manifests were proven byte-identical to the base commit: PREEXISTING. No suppressions or risk exceptions.
- SonarQube Cloud: BLOCKED_ACCESS (CloudFront 403 before login); no project, token or analysis configured.

CLI scans ran locally because Docker is absent. Published PR: https://github.com/JuanCopado/Emergency/pull/22.

First GitHub container run: https://github.com/JuanCopado/Emergency/actions/runs/43993493281. Rule and report tests passed; scan output/cache writes failed because capability-dropped root did not own the mounted runner directories. This is an infrastructure failure, not a vulnerability-only failure. The workflow now runs containers with the host UID/GID, Semgrep writable configuration in `/tmp`, and Trivy cache at `/cache`. The corrected run must be observed separately; this first failed run is preserved.

## Blocking findings

Each row is an advisory occurrence, not a distinct exploitable incident. Exposure, reachability and recommended upgrade paths require dependency review. Owners remain UNASSIGNED; no assignment to another person is invented.

| Priority | Severity | Advisory | File | Package | Installed | Fixed versions reported | Owner | Next action |
|---|---|---|---|---|---|---|---|---|
| P1 | HIGH | CVE-2026-93749 | app/package-lock.json | source-map-js | 1.2.1 | 1.2.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | CRITICAL | CVE-2026-104848 | app/package-lock.json | tinypool | 1.1.1 | 2.1.1 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | CRITICAL | CVE-2026-104849 | app/package-lock.json | tinypool | 1.1.1 | 2.1.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-109383 | app/package-lock.json | undici | 8.11.2 | 6.29.1, 7.30.1, 8.12.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-109829 | app/package-lock.json | undici | 8.11.2 | 7.30.1, 8.12.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-109869 | app/package-lock.json | undici | 8.11.2 | 6.29.1, 7.30.1, 8.12.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-87018 | app/package-lock.json | undici | 8.11.2 | 6.29.1, 7.30.1, 8.12.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-112942 | app/package-lock.json | vite | 5.4.21 | 8.3.3, 8.2.4, 8.1.6, 7.3.7, 6.4.4 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | CRITICAL | CVE-2026-47429 | app/package-lock.json | vitest | 2.1.9 | 4.1.0, 3.2.6 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-115572 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-115580 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-115585 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.2 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119203 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.4 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119204 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.4 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119205 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.4 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119206 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.3 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119207 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.3 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119208 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.3 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |
| P1 | HIGH | CVE-2026-119209 | clinical/requirements-test.txt | pypdf | 6.20.0 | 6.21.3 | UNASSIGNED | Review dependency chain and prepare a tested upgrade PR |

The complete metadata list, including lower severities, is in `baseline.json`. None is ignored by the CI gate. No package versions, clinical formulas, modules, accepted contracts or evidence states were changed.

## Adoption limits

The task branches from the latest published integration base, not main. The newer R2/E1 uncommitted local candidate is preserved and is not republished by this CI task. Existing Clinical QA/App UI QA workflows remain byte-identical to that base.

The schedule is configured but cannot run weekly until the workflow reaches GitHub’s default branch through an authorized integration. A PR alone does not activate it. No branch protection or required-check setting was changed.

Sonar setup must resume from an accessible authenticated session. No dummy keys/properties or skipped green Sonar job were added. See README.md for the exact remaining work.
