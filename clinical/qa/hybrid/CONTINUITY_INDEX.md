# v1.44 — L02 continuity index

CLINICALLY_PENDING. Runtime parent 42b7d2bbc4acaa19c5072ad9a5fccbbaa19de95d.
This is a technical snapshot, not clinical approval.

| Layer | Input within this baseline | Interpretation |
| --- | --- | --- |
| Source audit 18 October 2026 | ../global-medication-audit-v144/counts.json and selected JSON sources in HANDOFF_MANIFEST.json | 252 named substances + 18 complex entities; 3 P1 at that date |
| Follow-up 25 October 2026 | supplements/reconciliation-20261018/structured-fields-20261025/current-statistics.json | 255 names + 18 complex entities; 273 queued entities; 4 P1 |
| Current findings | supplements/reconciliation-20261018/structured-fields-20261025/current-findings.json | GMA-P1-001, GMA-P1-002, GMA-P1-003 and GMA-C-P1-001 remain open |
| Current status | supplements/reconciliation-20261018/structured-fields-20261025/V1.44_CURRENT_AUDIT_STATUS.md | Semantic global audit incomplete; no new browser run or professional approval |
| Original task scopes | task-cards/C01.md through C05.md | Prepared, not started; later dispatch requires exact execution commit |

222 source records are not 222 reconciled unique clinical regimens.
46 acute contracts comprise 27 calculable contracts and 19 permanently blocked contracts.
58 historical scenarios comprise 39 calculable scenarios and 19 expected blocks; do not confuse scenarios with contracts.
89 outpatient pediatric IDs and 1061 browser scenarios retain their historical dates.
133 UI, 116 export and 201 individual automated evidence counts are source-record metrics, not clinical approvals.
19 blocked contracts remain blocked. Products/local protocols and named, dated medical/pharmacy approvals remain pending.
L00-S remains pending with storage risk accepted by the owner.

No automatic incorporation of the original 43 pending files occurred. Selection and exclusions are explicit in HANDOFF_MANIFEST.json.
The original repository and historical frozen references remain outside this isolated clone and unchanged.
