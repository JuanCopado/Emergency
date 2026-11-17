# Security and quality

Task date: 16/11/2026. Base: `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`
on `codex/v144-international-scope-20261116`. This is infrastructure for the
international core, independent of language, hospital or jurisdiction.
Clinical arithmetic, accepted contracts, evidence states and `CLINICALLY_PENDING`
are unchanged. Publishing this task does not integrate the local R2/E1 candidate.

## Execution

`.github/workflows/security-and-quality.yml` adds two independent jobs, without
altering Clinical QA or App UI QA. It runs on PRs and pushes to `main`, `master`,
`codex/**` and `v1.*`, plus manual dispatch and a weekly Monday 07:23 UTC schedule.
Concurrency cancels superseded push/PR work on the same repository and head
branch; it does not guarantee that two very short completed runs cannot occur.

**GitHub schedules run from the default branch only.** The default is still
`main`; this unmerged PR cannot activate the weekly schedule or make its manual
dispatch discoverable there. No protected branch was changed to work around
that requirement. Push and PR executions exercise the candidate now. Full
adoption across branches and weekly activation require normal integration of
the workflow into the relevant branches/default branch.

## Scope and immutable dependencies

`toolchain.lock.json` records official action SHAs, registry image digests and
versions. The workflow invokes scanner images directly with Docker, instead of
using trivy-action and its additional transitive actions. Source mounts are
read-only; no persisted Git credentials or application secrets are supplied.
Semgrep has no network during its execution; metrics and version checks are off.
Trivy telemetry/version checks are off; it downloads public advisory/check data.
Advisory databases intentionally update, while executable tools remain pinned.

- Semgrep 1.185.0: 12 local rules, with positive and negative fixtures. Coverage
  includes dynamic evaluation, shell execution, unsafe deserialization/YAML,
  TLS verification, interpolated SQL, raw HTML, wildcard postMessage and weak
  randomness. These are focused security checks, not an exhaustive SAST policy
  or proof of absence of bugs. All findings fail the job, including warnings.
- Trivy 0.76.2: `vuln,secret,misconfig`, all severities visible, development
  dependencies included, unfixed issues retained. Custom filename detection
  includes `clinical/requirements-test.txt`. HIGH/CRITICAL findings and every
  secret fail the final gate. Its scanner step writes all results with exit 0
  **only for findings**; infrastructure errors still fail. The explicit report
  gate then enforces severity. There is no `continue-on-error`.
- Trivy verifies the three required dependency targets in its output. Python
  requirements cover declared pinned packages; their transitive dependencies
  are not completely locked here and are not claimed as fully covered.
- No Dockerfile/IaC configuration files were found in the first Trivy scan.
  The misconfiguration scanner is enabled for future supported configuration;
  it is not a substitute for actionlint on GitHub workflows.
- Local actionlint 1.7.12 validates the new workflow. Existing technical QA
  continues to check types, lint, tests, build and clinical contracts.

No patient records or private backup stores are inputs. Exclusions cover
downloaded dependencies, build/cache/graph outputs, preservation/backups and
binary documents/archives/medical images. The three generated clinical JSON
catalogs are excluded only from Semgrep because they are data, not source code;
they remain subject to their existing generators/QA. Synthetic rule fixtures
are tested separately, not counted as product findings. No source directory or
dependency manifest is excluded to hide vulnerabilities.

## Reporting and baseline

`scripts/security/report.py` publishes only allowlisted metadata (rule/advisory
ID, file, line, severity, package versions, fingerprint and triage fields).
Raw reports can contain code or secret matches and stay on the ephemeral runner;
they are never uploaded. Public artifacts contain only `*.summary.json`, retained
for seven days. Errors/missing reports or missing required targets fail closed.
Adversarial tests verify that matched secrets, snippets and messages are omitted.

`baseline.json` records initial findings in files proven byte-identical to the
base commit. It classifies existing findings; it does not ignore or accept risk.
Future unmatched fingerprints are `NEW_OR_CHANGED`. Attribution is relative
to this initial snapshot, not a full historical/git blame analysis. Owners are
`UNASSIGNED` pending a real assignment; P1 covers blockers, P2 lower severities.
No exception is approved. Any future exception must record scope, justification,
owner and review date, and must not be created solely to obtain a green check.

## SonarQube Cloud — BLOCKED_ACCESS

The repository was verified public and the connected GitHub account has admin
permission. The cloud browser received a CloudFront 403 `Request blocked` at
`https://sonarcloud.io/`, including after one reload, before sign-in or project
selection. Organization, plan, existing project keys and Sonar permissions could
not be verified. No OAuth permission, import, token, GitHub secret, analysis-method
change, billing change or Sonar analysis was performed. No credential was exposed.

There is intentionally no fabricated `sonar-project.properties` and no skipped
Sonar job presented as successful. Resume in an accessible authenticated session:
verify organization/visibility/plan and actual project keys; import only Emergency;
select Actions and disable automatic analysis for that project; create the
least-privileged supported token directly in GitHub Actions secrets; configure
explicit source/test/generated scopes; reuse real coverage if available; pin the
official scan action and wait for the quality gate. Never purchase a plan or
make this project public as a workaround. Do not pass its token to fork PRs.

The free plan documentation limits ordinary branch analysis to the main branch
and PRs targeting it; account/project eligibility must be checked during resumption.
No claim of compatibility with every Emergency integration branch is made.

## Reproduction

Use the exact commands and digests in the workflow. For local validation with
the same CLI versions:

```sh
actionlint -shellcheck= .github/workflows/security-and-quality.yml
python3 -m unittest discover -s security/tests -p 'test_*.py'
semgrep --test --config security/rules security/tests --metrics off --disable-version-check
semgrep scan --config security/rules --metrics off --disable-version-check --strict --error --json --output /tmp/semgrep.raw.json .
trivy fs --config security/trivy.yaml --scanners vuln,secret,misconfig --disable-telemetry --skip-version-check --include-dev-deps --ignore-unfixed=false --format json --output /tmp/trivy.raw.json .
python3 scripts/security/report.py semgrep /tmp/semgrep.raw.json /tmp/semgrep.summary.json --check --require-target app/src/main.tsx --require-target clinical/scripts/clinical_note_api.py
python3 scripts/security/report.py trivy /tmp/trivy.raw.json /tmp/trivy.summary.json --check --require-target app/package-lock.json --require-target clinical/requirements.txt --require-target clinical/requirements-test.txt
```

The initial local environment had no Docker runtime; the verified pinned CLI
versions were used locally. Container execution is validated separately in Actions.
