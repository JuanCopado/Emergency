# Codex bootstrap — Emergency v1.42

This file defines the safe entry point for Codex work on this repository.

## Repository and branch guard

- Repository: `JuanCopado/Emergency`
- Working branch: `v1.42-codex-consolidation`
- Baseline commit used to create this consolidation branch: `bcb05891c6e95499acf1d20ba4388dcc5aed5766`
- Never modify, merge into, reset, or force-update `main`.
- A newer HEAD on `v1.42-codex-consolidation` is expected after legitimate commits. Do not reset it back to the baseline merely because the SHA differs.

Before editing, run:

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short
```

If the active branch is not `v1.42-codex-consolidation`, stop and diagnose before editing.
If the working tree is unexpectedly dirty, stop and inspect the changes before editing.

## Mandatory reading order

1. `CODEX.md`
2. `clinical/AGENTS.md`
3. `clinical/CURRENT_STATE.md`
4. `clinical/qa/V1.41_FINAL_HANDOFF.md`
5. `clinical/qa/V1.41_PROCEDURES_STATUS.md`
6. `clinical/qa/V1.41_PROCEDURE_GAP_AUDIT.md`
7. `clinical/SKILL.md`
8. `clinical/MODULES.md`
9. `clinical/VALIDATION.md`
10. `clinical/references/evidence-registry.json`

Treat older snapshots embedded in continuity files as historical unless the current branch explicitly promotes them.

## Clinical safety and governance

- Do not invent doses, concentrations, contraindications, compatibilities, evidence, stock, protocols, or validation status.
- Preserve source discrepancies and flag them for review.
- Automated tests and QA do not equal prospective clinical validation.
- Never promote YELLOW to GREEN automatically.
- For changing/high-risk clinical recommendations, verify current primary/authoritative sources before changing clinical content.
- Keep deterministic arithmetic separate from clinical indication/selection.
- For Portugal/Azores claims, distinguish verified DGS/INFARMED/local information from assumptions.
- Do not duplicate scores, formulas, modules, or procedures when a canonical implementation exists.

## Procedures and visuals

- Current v1.41 procedure model: 200 textual IDs, 196 canonical procedures, 4 aliases, 16 families.
- All procedures remain YELLOW unless explicitly reviewed and promoted under project governance.
- Physician visual layer is separate from the canonical procedure text.
- Do not use Picsart.
- Do not regenerate an accepted visual without checking its control/QA status and canonical procedure first.
- Visual QA is not clinical validation.

## Development workflow

For broad tasks, begin with a read-only plan/audit. Do not perform a repository-wide refactor before mapping architecture, contracts, tests, and clinical governance.

Preferred implementation sequence after an approved plan:
1. architecture/types/contracts;
2. backend/API;
3. frontend;
4. tests;
5. clinical/evidence QA;
6. export/print/PDF;
7. procedures/visual layer;
8. cleanup/documentation.

Before each commit:
- inspect `git diff`;
- run the relevant tests/validators;
- report exactly what was and was not executed;
- update continuity/evidence/changelog files when required by `clinical/AGENTS.md`.

Never claim a test, workflow, or clinical QA passed unless it was actually run and its result was observed.

## Cross-branch material

`v1.39.1-clinical-note-hardening` may contain useful clinical-note hardening work. Compare it selectively. Do not merge or cherry-pick it wholesale without first auditing the diff and contracts.

## Initial Codex mission

The first v1.42 task is a repository-wide, read-only audit and consolidation plan. Inventory architecture, modules, procedures, scores/calculators, pharmacology, pediatrics, ECG/POCUS/imaging, clinical note/governance, evidence, frontend, contracts, export/PDF, tests, security, and technical debt.

Classify findings P0/P1/P2/P3. Stop after the plan unless implementation has been explicitly authorized.
