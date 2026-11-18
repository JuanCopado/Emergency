# Picomatch containment — 18/11/2026

Scope: technical build containment for the international core. Owner accepted the
containment approach in this session. Base: PR24 at
`ce808a63f3f68c8750fd48c425d4d95bbe3f4de3`, exact source tree
`82d01340c98cbf72cc79307b2f5ca5d19ad07974` (1,051 verified blobs).
No clinical arithmetic, contracts, source evidence or clinical states are changed.
`CLINICALLY_PENDING` is preserved. No merge or deployment is performed.

## Controls

- Every ordinary Vite production build checks that all picomatch lock entries
  remain development-only. It rejects picomatch in emitted application modules,
  including nested Windows/POSIX paths, virtual modules and external imports.
- App UI QA now runs `build:security` with `EMERGENCY_SECURITY_AUDIT=1`.
  This also generates and checks source maps for the service worker and its
  separate Workbox runtime, which are outside the application Rollup graph.
  Missing/empty/malformed maps fail closed. The check considers sourceRoot.
- Source maps are diagnostic CI outputs on the disposable runner. Ordinary
  builds do not generate these audit maps. No build artifact is deployed here.
- The existing App UI QA job uses a pinned checkout with no persisted Git
  credentials. npm lifecycle scripts are disabled, matching the already used
  coverage installation. Permissions remain contents:read; no secret is added.
- Build/test glob patterns remain repository-controlled literals. File uploads
  and HTTP input must not become matcher patterns or build configuration.
  The application is distributed from production build output, not a public
  development/test server.

The hosted CI job is ephemeral and separate from patient data. Its network is
not disabled: package installation, Actions and artifact transfer need network
access. This containment does not claim an offline sandbox, comprehensive
reachability analysis, or protection against a malicious compiler/source-map
producer. Tests use synthetic fixtures, not patient records.

## Advisory remains open

Both reported HIGH records are CVE-2026-112366 / GHSA-fc5q-39xc-vjpf, on
picomatch2.3.2 and4.0.7. All five installed lock nodes for those two versions
are development-only in the inspected base. An upstream patch proposal is still
open; the reviewed advisory lists no fixed release. No dependency is renamed,
patched or excluded to change scanner output. Baseline, Trivy dev-dependency
scanning and HIGH/CRITICAL gates remain unchanged. Containment is not remediation
of the package and is not a risk exception or permission to override the gate.

References:
- https://github.com/advisories/GHSA-fc5q-39xc-vjpf
- https://github.com/micromatch/picomatch/pull/238

## Verification

Local Windows/Node24:22 containment checks PASS,8 existing report privacy/failure
tests PASS, actionlint1.7.12 PASS for the affected workflow (shellcheck absent),
and git diff --check PASS. The same test cases run under Vitest for measured
coverage, with two additional real Vite build fixtures (clean and contaminated).
Full Node22/Linux build, worker-map inspection and remote QA remain pending at
this implementation cut; their results must be observed separately.

Close the package findings only after a verified fixed dependency/approved
replacement and a fresh scanner result. Preserve the distinction between
technical containment, package remediation, clinical review and deployment.
