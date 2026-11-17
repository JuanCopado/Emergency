# SonarQube Cloud continuation - 17/11/2026

Scope: infrastructure for Emergency's international core. No clinical content,
arithmetic, sources, contracts or evidence state changed. CLINICALLY_PENDING.

- PR: https://github.com/JuanCopado/Emergency/pull/22
- Verified task HEAD before editing: `3be9422ff3562516429412aa2fafeab720e2386b`.
- Base/integration: `codex/v144-international-scope-20261116` at
  `1d0652ebcef9b5990edd9e5745b0c06f8d6b8274`.
- Exact isolated source copy: all 1,042 blobs and tree
  `2cc3efc5ecc16601c26b41473b64933805beb9b7` checked against GitHub Git data;
  original HEAD reconstructed and SHA-verified, local history intentionally shallow.
- Terminal network DNS was unavailable; authenticated local Chrome downloaded
  the branch archive, and the GitHub connector supplied immutable Git metadata.
  No other worktree or uncommitted R2/E1 candidate was edited or published.
- Existing project: https://sonarcloud.io/project/overview?id=JuanCopado_Emergency
- Active account: Juan Copado; organization administration and project settings
  accessible; existing public project bound to the correct GitHub repository.
- Verified onboarding keys: `JuanCopado_Emergency` and `juancopado`.
- Automatic Analysis: OFF for this project, observed after switching.
- Existing Team trial: premium access ends 30/11/2026. Current integration branch
  and PR are eligible during Team access. A future Free downgrade excludes this
  non-main target; no plan change was made or promised.
- SONAR_TOKEN: installed directly as an encrypted repository Actions secret after
  user confirmation. Scoped token: Emergency only; Browse + Execute analysis;
  expires 17/12/2026; no Administer projects or organization-wide access. The
  earlier exposed onboarding token was never reused and has been revoked; the
  personal-token table then showed no tokens. No credential value is recorded.
- The first Actions attempt failed closed because SONAR_TOKEN was missing.
  After installation, the same Sonar job was re-run; its credential and full-
  history checkout steps passed. Scanner and quality gate result recorded below.
- Prior Automatic Analysis is historical: the existing main overview showed 18
  issues, security C, no coverage data and gate not calculated. The pre-existing
  Sonar bot comment on PR #22 reported gate failure (new-code security D); that
  comment is not evidence of the new Actions job running.
- No coverage.xml, lcov.info or coverage-final.json exists in the verified source
  snapshot. No coverage result is claimed.

## Observed Actions analysis

Source revision: `f982813830e7960f4914aa4849e52887f53cc18b` (scanner SCM revision).
Run: https://github.com/JuanCopado/Emergency/actions/runs/44001459122/attempts/2
Sonar job: https://github.com/JuanCopado/Emergency/actions/runs/44001459122/job/133771701766
Project/PR: https://sonarcloud.io/dashboard?id=JuanCopado_Emergency&pullRequest=22

- Authentication, full-history checkout and scanner startup: SUCCESS.
- Official scanner 8.4.0.16527 GPG signature verification: SUCCESS; not disabled.
- Scope: 285 files indexed, matching the 201 source/configuration + 84 test
  files in the local scope audit. PR analysis targets the international branch.
- Analysis report generated, compressed and uploaded: SUCCESS.
- Server quality gate awaited: FAILED at 02:28:46 UTC on 17/11/2026. This is a
  real gate failure, not a missing credential, plan denial or scanner setup error.
- Two failed conditions observed in the refreshed PR UI for the exact revision:
  security rating C (required A) and reported new-code coverage 0.0% (required
  at least 80.0%; 68 new lines to cover). No coverage report was supplied; this
  is not a measurement of the coverage achieved by the separate test suites.
- Two open security findings in `scripts/security/report.py`, lines 76 and 92,
  titled "Path traversal through faulty LLM-provided CLI arguments in report.main()".
  These are scanner findings awaiting triage of the CLI trust boundary, not a
  claim of independently confirmed exploitability. No issue was accepted,
  dismissed, suppressed or fixed just to turn the gate green.
  https://sonarcloud.io/project/issues?pullRequest=22&open=AaHnD2ucjhN_TZ0KNPMZ&id=JuanCopado_Emergency
  https://sonarcloud.io/project/issues?pullRequest=22&open=AaHnD2ucjhN_TZ0KNPMa&id=JuanCopado_Emergency
- Remaining analyzer warning: Python target version is not configured; the
  analyzer defaults to compatibility with Python 3.10 through 3.15. No unsupported
  runtime version guarantee is inferred or configured merely to remove the warning.
- Semgrep: SUCCESS. Trivy: scan completed, gate FAILURE for 50 findings; preserved.
- Clinical QA for the source revision: SUCCESS in PR run 44001459201 and push
  run 44001453168. This remains technical QA, not prospective clinical validation.

The earlier missing-secret attempt and historical Automatic Analysis results are
retained as separate observations. This continuation resolves configuration and
authentication, not the new-code security/coverage findings.

## Validation

- actionlint 1.7.12 Windows ARM64: PASS (`-shellcheck=`; shellcheck unavailable).
  Official release archive SHA-256:
  `cadcf7ea4efe3a68728893813643cebe1185e5b1d4be5b96245f65c9a4d5ea41`.
- Existing security report/privacy/failure-propagation tests: 4/4 PASS.
- Existing CI regression tests (`test_ci_v142.py`): 8/8 PASS.
- Scope audit: 201 source/configuration files and 84 test files, disjoint;
  all executable/configuration files outside preservation are covered. The
  remaining 757 files are outside executable source scope. Existing Semgrep
  and Trivy job definitions compare equal to the original parsed workflow.
- No dependency upgrades, duplicate scanner installation, workflow replacement,
  protected-branch writes, merge, deployment or clinical validation performed.
- Existing Semgrep/Trivy definitions remain unchanged. The previously observed
  Trivy gate (3 CRITICAL, 16 HIGH, 26 MEDIUM, 5 LOW) is not suppressed.
- Weekly cron remains pending default-branch adoption; publishing this PR does
  not activate it.

## Owner plan decision

Use the existing free Team trial until its end on 30/11/2026, then Free; no paid
plan authorized. A one-time review/action attempt is scheduled for 29/11/2026
morning, Atlantic/Azores. This is not proof that the billing plan has changed.
Check impact on the organization's other private projects before a plan-wide
downgrade, and prepare Free-compatible credentials because scoped organization
tokens require Team/Enterprise. Preserve repository visibility, main/default
branch, PR base and protections. The Free restrictions on our integration branch
are not bypassed by relabeling it as main.

## Official references

- Action release: https://github.com/SonarSource/sonarqube-scan-action/releases/tag/v8.5.0
- Tag SHA: https://api.github.com/repos/SonarSource/sonarqube-scan-action/git/ref/tags/v8.5.0
- Plans: https://docs.sonarsource.com/sonarqube-cloud/administering-sonarcloud/managing-subscription/subscription-plans
- Scoped tokens: https://docs.sonarsource.com/sonarqube-cloud/administering-sonarcloud/managing-organization/scoped-organization-tokens
- Explicit scanner configuration: https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/scanners/sonarscanner-cli
