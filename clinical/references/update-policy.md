# Living Evidence update policy

## Objective
Keep high-risk emergency recommendations current without allowing uncontrolled automatic rewriting of clinical guidance.

## Workflow

### A. Detect
For Portugal, include the DGS and INFARMED sources and reconciliation rules in
`portugal-context.md`. Record inaccessible sources and unverified local applicability.

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

### D. Do not auto-promote
New evidence must first enter `updates/pending-updates.json`.

Promote into stable modules only when:
1. source is authoritative enough for the claim,
2. recommendation is applicable to emergency care,
3. conflicts have been reconciled,
4. dosing calculations and contraindications are validated,
5. affected test cases pass.

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
