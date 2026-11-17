# Security and quality

Task date: 16/11/2026. Base: `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`
on `codex/v144-international-scope-20261116`. This is infrastructure for the
international core, independent of language, hospital or jurisdiction.
Clinical arithmetic, accepted contracts, evidence states and `CLINICALLY_PENDING`
are unchanged. Publishing this task does not integrate the local R2/E1 candidate.

## Execution

`.github/workflows/security-and-quality.yml` adds three independent jobs, without
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
read-only; no persisted Git credentials or application secrets are supplied to
Semgrep or Trivy. Only the Sonar credential check and scan receive SONAR_TOKEN.
Containers run with the runner UID/GID, so their writable report/cache mounts
work with all Linux capabilities dropped. Semgrep configuration/cache uses `/tmp`;
Trivy uses the explicit `/cache` mount rather than a root-owned home directory.
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
catalogs are excluded from Semgrep and Sonar because they are data, not source code;
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

## SonarQube Cloud - Actions connected

The authenticated local Chrome session was used on 17/11/2026. Emergency already
exists, is public and is bound to JuanCopado/Emergency. No duplicate was imported.
Its GitHub Actions onboarding page provided the actual keys
`sonar.projectKey=JuanCopado_Emergency` and `sonar.organization=juancopado`.
Project and organization administration controls are available to Juan Copado.
Automatic Analysis was switched OFF only for Emergency; Actions is configured
in this workflow. The previous CloudFront 403 is historical, not a current blocker.

The organization is on an existing Team trial, with premium access ending
30/11/2026. Team permits branch analysis and PR analysis against our international
integration branch. After a downgrade to Free, ordinary branch analysis is
limited to the project's main branch, and PR analysis to PRs targeting that branch.
PR #22 targets `codex/v144-international-scope-20261116`, so it would not qualify
under those Free-plan restrictions. No subscription, payment, visibility,
default-branch or branch-protection change was made. Future plan errors must
remain visible and must not be reported as code findings or a passing gate.

SONAR_TOKEN is now stored as an encrypted repository Actions secret. The user
approved creation of a scoped organization token restricted to Emergency with
Browse (for gate status) and Execute analysis, without project administration or
organization-wide access. It expires 17/12/2026. The onboarding token exposed in
an earlier UI observation was not reused and was revoked; the personal-token
table subsequently showed no tokens. No credential value is stored in repository
files, commits or reports.

The owner selected the remaining free Team trial, followed by Free. A review is
scheduled for the morning of 29/11/2026 in Atlantic/Azores, before trial expiry.
This schedules a review/action attempt, not an already completed downgrade.
It must check the other private projects in the same organization before a
plan-wide change. Scoped organization tokens require Team/Enterprise, so a
Free-compatible authentication method must also be prepared during transition.

`sonar-project.properties` classifies executable/configuration sources, Python
tests, Vitest tests and browser checks explicitly. Scanner automatic configuration
is disabled so it cannot override those boundaries. Generated clinical JSON,
dependencies, build/cache outputs, archives and preservation/backups are excluded
because they are derived data or outside executable source scope. Clinical
canonical documents/data and private backup stores are not scanned. Source files
are not excluded because of findings; synthetic security fixtures are test code.
No coverage XML/LCOV report exists in this exact snapshot; no coverage percentage
or coverage exclusion was invented.

The authenticated Actions scan at revision `f982813830e7960f4914aa4849e52887f53cc18b`
completed and uploaded its report. Its awaited quality gate FAILED: new-code
security C instead of A, and reported coverage 0.0% instead of at least 80.0%.
Two open path-traversal findings in `scripts/security/report.py` require trust-
boundary triage; no coverage report was supplied to Sonar. Configuration is
connected, but findings and coverage remain unresolved. No gate or rule was
relaxed. See the detailed observed run and limitations in the setup report.

SonarSource sonarqube-scan-action v8.5.0 is pinned to verified full commit
`59202af334b4ba7b5db01b701b8e79f8b3bef0f4`; it retains the action's scanner
signature verification and waits up to 600 seconds for the quality gate.
Checkout fetches full history and does not persist credentials. Sonar has no
dependency on Trivy and receives only read permission for GitHub contents.
Fork and Dependabot events emit an explicit OMITTED warning/summary and never
receive SONAR_TOKEN. Missing credentials fail as CONFIGURATION_ERROR; scanner
or gate failure is not suppressed. No pull_request_target trigger is used.

Observed results and the plan transition are recorded in
[SONAR_SETUP_2026-11-17.md](SONAR_SETUP_2026-11-17.md). Technical QA does not
change clinical acceptance or CLINICALLY_PENDING.

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
