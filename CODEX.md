# Codex bootstrap — Emergency v1.44 functional validation

La validación clínica del proyecto corresponde al Dr. Juan Copado Ceballos. Preparar la evidencia y presentar una pregunta SÍ/NO por decisión según `AGENTS.md`. Farmacia es consultiva.

This file defines the safe entry point for Codex work on this repository.

## Current owner execution directive: reviewed contracts (2026-11-16)

The later explicit physician-owner request accepts the completed clinical work and authorizes implementation and removal of the inherited permanent blocks. Read the current directive in `AGENTS.md`, `clinical/references/acute-contract-owner-acceptance-2026-11-16.json` and `clinical/qa/REVIEWED_ACUTE_CONTRACT_RELEASE_2026-11-16.md`. The authorized task branch is `codex/v144-reviewed-contracts-enable-20261116`, based on verified international HEAD `062d890b4fc92369b83c87664bb4bb0205ccb33f`. This supersedes older instructions to retain all19 permanent blocks for this reviewed scope. Do not request the already recorded owner acceptance again or infer another professional's signature. Preserve case-specific gates, source boundaries, protected branches and the overall release status. Implementation, relevant verification and task publication are authorized; a published branch is not an installed deployment.

## Current owner directive: international scope (2026-11-16)

Read `AGENTS.md`, `docs/INTERNATIONAL_SCOPE.md` and `STATE.md` first. Emergency is an international, extensible acute-care platform with a coherent global clinical core and the same canonical module/algorithm across settings. The core works without a selected hospital; never infer country or hospital from biography or interface language. Context-specific evidence and hospital experience retain their scope and provenance.

The owner requested the necessary scope and coordination changes. The original scope delivery used the isolated branch `codex/v144-international-scope-20261116`, based on verified commit `926649ac5b3168267839f987de77a62401b5e7da`. It is permitted for this directive, documentation, context-neutral wording and product presentation. Preserve clinical arithmetic, evidence states and existing blockers; this dispatch does not authorize merging protected branches or transferring clinical data to external services.

The INT-02A clarification continues on that branch from verified commit `285114a56ce2814b54b53d990474bb121876ef84`. Apply `clinical/references/international-guideline-policy.md`: choose broadly recognized international guidance by quality, currency, consensus and population/indication. Compare applicable primary sources and incorporate only materially justified clinical, safety, regulatory/product or resource exceptions, preserving the complete regimen, provenance, clinical review and actual status. The territorial catalog supports comparison, not automatic geographic priority or complete country protocols; do not universalize NICE/AHA.

## Repository and branch guard

- Repository: `JuanCopado/Emergency`
- Working branch: `v1.44-clinical-functional-validation`
- Frozen baseline: `v1.42-rc1 @ 0fa17bf16864bb7b371b323b8557c63bc29ca4c2`. Preserve both `v1.42-rc1` and `v1.42-codex-consolidation` at that SHA.
- Never modify, merge into, reset, or force-update `main`.
- A newer HEAD on `v1.44-clinical-functional-validation` is expected after legitimate commits. Do not reset it back to the baseline merely because the SHA differs.

Before editing, run:

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short
```

The owner-authorized isolated L02 technical branch `codex/v144-hybrid-baseline` is also permitted for baseline preparation only; C01–C05 and publication remain unauthorized.
The current international-scope dispatch above is an explicit task exception. For another branch, verify the applicable owner dispatch and base before editing; the historical L02 restriction is not a statement that later authorized task publications remain forbidden.
If the working tree is unexpectedly dirty, stop and inspect the changes before editing.

## Mandatory reading order

1. `AGENTS.md`, `docs/INTERNATIONAL_SCOPE.md`, `STATE.md`, then `CODEX.md`
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
- Apply the equivalent source and product checks to the jurisdiction actually selected. A missing hospital profile limits the dependent operational claim, not the international project's entire core. Use `clinical/references/international-context.md`.
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

## Current phase and historical initial mission

The user closed v1.43 at 737bb1b8dce5ffbdb296bb0c99d134ea318c8298 and authorized v1.44 synthetic functional validation from that exact commit. Read clinical/qa/V1.43_UI_UX_FINAL.md and the v1.44 validation matrix. Preserve the v1.43 closure branch. Read `clinical/qa/V1.43_UI_UX_AUDIT.md` for the audit, ten procedure layouts, screenshots, tests and remaining limits. Preserve clinical logic and evidence states. Scores remain textual; 186 procedures remain outside the ten-layout visual pilot. No clinical image is approved by this UI audit.

The historical first v1.42 task was a repository-wide, read-only audit and consolidation plan. Its later authorized implementation and technical freeze are documented in `clinical/qa/V1.42_RC1_FREEZE.md`.

Classify findings P0/P1/P2/P3. Stop after the plan unless implementation has been explicitly authorized.
