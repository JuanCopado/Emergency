# L02 — isolated technical baseline

Status: CLINICALLY_PENDING. Runtime parent: 42b7d2bbc4acaa19c5072ad9a5fccbbaa19de95d.
The owner authorized building this isolated technical branch, codex/v144-hybrid-baseline.
No C01–C05 execution, push, clinical change, evidence promotion or release closure is authorized.

Read HANDOFF_MANIFEST.json and CONTINUITY_INDEX.md before a task card.
The immutable execution commit is recorded by a separate local dispatch manifest after committing.
Do not use origin/main or assume the runtime parent includes uncommitted supplemental files.
C01–C05 remain NOT_STARTED / BLOCKED_UNTIL_PUBLICATION_AND_DISPATCH_AUTHORIZATION.

The original five task cards are byte-preserved in task-cards/. Their input paths and acceptance criteria remain valid.
For C03, no new print invocation means no call to window.print; it does not require removal of the pre-existing print portal.
For C02, DOM keyboard tests do not certify real-browser accessibility.
For C05, unavailable browser means BLOCKED visual verification, not PASS.

The literal branch guard in CODEX.md permits this isolated technical branch only in addition to the existing v1.44 branch.
Future task branches require explicit owner dispatch authorization naming their branch and the final execution SHA.
Tasks may write only their assigned path. Shared dependencies stay read-only. Report a production defect rather than expanding scope.
No change to main, RC1, v1.43, dosing, units, concentrations, formulas, gates or clinical decisions is authorized.

A locked dependency install and existing focused tests are base-readiness checks only. They do not begin a C-task or add its missing cases.
The publication remote has a disabled push URL locally. Publication requires specific later authorization and the exact verified SHA.
No credentials, local node_modules, caches, virtualenvs, refs/codex, backup archives or private dumps belong in the handoff.
