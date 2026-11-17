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
- SONAR_TOKEN: absent from repository Actions secrets. The onboarding token was
  exposed by a UI observation and must be revoked, not reused. Replacement:
  Specific projects = Emergency only; Browse + Execute analysis; finite expiry;
  no Administer projects. Creation awaits the required credential intervention.
- New CI scan / quality gate: NOT EXECUTED until a valid credential is installed.
- Prior Automatic Analysis is historical: the existing main overview showed 18
  issues, security C, no coverage data and gate not calculated. The pre-existing
  Sonar bot comment on PR #22 reported gate failure (new-code security D); that
  comment is not evidence of the new Actions job running.
- No coverage.xml, lcov.info or coverage-final.json exists in the verified source
  snapshot. No coverage result is claimed.

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

## Official references

- Action release: https://github.com/SonarSource/sonarqube-scan-action/releases/tag/v8.5.0
- Tag SHA: https://api.github.com/repos/SonarSource/sonarqube-scan-action/git/ref/tags/v8.5.0
- Plans: https://docs.sonarsource.com/sonarqube-cloud/administering-sonarcloud/managing-subscription/subscription-plans
- Scoped tokens: https://docs.sonarsource.com/sonarqube-cloud/administering-sonarcloud/managing-organization/scoped-organization-tokens
- Explicit scanner configuration: https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/scanners/sonarscanner-cli
