# EMERGENCY — Security perimeter hardening, 18/11/2026

Base: PR #23 isolated Sonar candidate at af87ff815665884103689c771ac0807b751a5883.
Task branch: codex/security-perimeter-hardening-20261118.

## Scope
- Fixed allowlist for 8 vetted official evidence surveillance hosts. The shared international clinical core is unchanged; adding future official sources requires explicit source/host review.
- HTTPS only, port 443, no URL credentials/fragments/control characters; reject private/reserved/loopback DNS results before opening the URL; no automatic HTTP redirects; bound the response to 5 MB.
- DNS preflight + default TLS validation are defense-in-depth, **not** a complete DNS-rebinding guarantee. Reverse proxy and egress firewalls remain deployment controls. An organization with a proxy-only network may have to provide a reviewed networking adapter; do not bypass the policy silently.
- Surveillance failures are explicit and never auto-update clinical recommendations. Exception strings are not echoed into audit reports.
- Clinical note HTTP adapter returns generic client error messages (422/500), correct 400 for malformed JSON, JSON-only responses with nosniff/CSP/no-referrer, and no request-line logging. No patient text or raw exception details reach error responses.
- The pediatric age/weight boundary returns one audited, static warning (`no matching age/weight band for regimen`) so the existing UI safety STOP remains visible. All other ValueError content remains redacted; synthetic regression tests cover both branches.
- Existing clinical diagnostic logic, calculator contracts, export formats, dose formulas, evidence registry and CLINICALLY_PENDING are unchanged.

## Verification requirements
New offline synthetic regressions exercise forbidden destinations, DNS/private IP, redirect policy, response caps, redacted error report, private exception text, malformed JSON, successful response schema and HTTP security headers. Run these and all existing Clinical QA + App UI QA + security scans on the exact branch SHA.

## Risks and non-claims
No real patient records or online evidence sites have been tested. The strict no-redirect policy could reject a site after a legitimate URL move; this must create a review signal, not follow a new destination implicitly. Loopback HTTP remains local-only by default. A future public-server deployment requires TLS termination and authorization controls outside this patch.
