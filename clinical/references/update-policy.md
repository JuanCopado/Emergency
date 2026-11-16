# Living Evidence update policy

## Objective
Keep high-risk emergency recommendations current without allowing uncontrolled automatic rewriting of clinical guidance.

Owner directive (2026-11-16, INT-02A): apply [international-guideline-policy.md](international-guideline-policy.md). Maintain one coherent international clinical core, selected by guideline quality, currency, international consensus and applicability. Compare Europe, the UK and the Americas where relevant; incorporate only verified material contextual differences, without duplicating whole modules or requiring a hospital profile for the common reference.

## Workflow

### A. Detect
Start with internationally recognized primary guidance relevant to the module.
Consult applicable national/product sources when a clinical, safety, product or
resource difference may change the decision. Use the source directory and scope
rules in `international-guideline-policy.md`; geography alone does not establish
priority. For a Portugal-specific dependency, include the DGS/INFARMED checks in
`portugal-context.md`. Record inaccessible sources and unverified applicability.

Search authoritative sources for:
- new guideline
- focused update
- safety alert
- major consensus statement
- practice-changing systematic review or RCT

### B. Classify
Assign:
- HIGH: may immediately alter emergency management, dose, contraindication, timing or disposition.
- MODERATE: may change preferred strategy but not immediate safety.
- LOW: contextual or confirmatory evidence.

### C. Compare
For every candidate update record:
- module
- current recommendation
- new recommendation
- source
- publication date
- strength/certainty
- clinical impact
- whether it changes bedside action
- the rationale for the common reference guideline and the exact population/indication
- whether the difference improves the shared core or requires a justified, limited variant
- the affected country/product/resources only where material to the decision
- the decision to implement, keep with justification, or leave unresolved, with source/version and review status

Do not stop at listing differences when evidence and context support a decision.
Implement the supported core correction or focused variant as a reviewable candidate
linked to the canonical module, preserving the complete source-supported regimen.
Do not average thresholds, mix incompatible regimen components, or create a full
protocol per country. A reference portal does not establish that its clinical
recommendations have been reviewed.

### D. Do not auto-promote
New evidence must first enter `updates/pending-updates.json`.

Promote into stable modules only when:
1. source is authoritative enough for the claim,
2. recommendation is applicable to emergency care,
3. conflicts have been reconciled,
4. dosing calculations and contraindications are validated,
5. affected test cases pass.

Retain the applicable clinical/pharmaceutical review and release process. Automated
surveillance proposes the exact change and affected scope; it does not activate a
new medication rule or grant cross-country approval. Coverage and acceptance apply
to the recommendation, population and context actually reviewed.

### E. Status rules
GREEN:
- recently checked,
- no newer authoritative source found,
- recommendation considered current.

YELLOW:
- review window exceeded,
- guideline old but not clearly replaced,
- relevant new evidence detected,
- publication/update status uncertain.

RED:
- newer authoritative guidance supersedes stored recommendation,
- safety warning materially affects use,
- stored dose/threshold/timing is no longer supported.

## Review cadence
- High-risk modules: every 30 days.
- Standard modules: every 90 days.
- Lower-change modules: every 180 days.
- Immediate re-check whenever the user asks for a protocol-level recommendation in a high-risk area.
