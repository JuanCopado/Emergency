# CI hook compatibility correction

Observed on PR129 initial HEAD44fb7a08992b023db98a06efb67efb4cd7b45f20: explicit-apply Windows/Linux and security policy tests failed because their exact-string policy recognized only the old picomatch prehook. The new predev/prebuild chain retained it after the purpose guard.

The validator and security regression now require that exact two-guard chain for dev/build, with the original guard required for every other product command. The documentary admission commands are named security:dermatology:check/test and are explicitly checked against their fixed reviewed implementation. No generic substring, OR chain, gate, threshold, scanner database, mitigation target or lock hash is relaxed. Clean-install CI must pass on the corrected SHA.

Windows local security tests also exposed that clearing the synthetic test environment removed SystemRoot, causing SSL context creation to fail before mocked HTTPS dispatch. The test fixture now preserves only this OS directory on Windows. TLS certificate and hostname verification remain enabled; no production diagnostic or credentials changed.

Observed after correction:39/39 security tests and15/15 admission lifecycle tests PASS; installation-check syntax valid. Initial remote and local failures/logs are retained. No clinical arithmetic, content, last_checked or approved decision changed. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
