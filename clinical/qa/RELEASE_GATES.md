# RELEASE GATES — v1.36

## Automated mandatory gate
Run from `clinical/`:

```bash
python3 qa/qa_runner.py
```

A non-zero exit code blocks merge/release.

## Human gate for high-risk modules
Before promoting a changed high-risk module to a release candidate, record:
- reviewer name/role;
- review date;
- authoritative source(s) and versions;
- unresolved disagreement, if any;
- Portugal/Azores applicability;
- local drug presentation/equipment/protocol checks when operational details are given;
- final decision: approve / approve with limitations / reject.

## Green-status rule
Automated QA may detect eligibility problems but **must never auto-promote a high-risk module from yellow to green**.

## Local-operational rule
A module containing a dose, electrical energy, infusion concentration, access-route rule or antidote/reversal instruction is not locally operational until the relevant formulary/equipment/protocol checks are complete.

## Merge rule
Changes to high-risk clinical content require:
1. automated QA PASS;
2. evidence registry updated;
3. update note/changelog;
4. human review record;
5. local reconciliation if the content claims Portugal/Azores operational use.
