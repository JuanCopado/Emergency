# RAG laboratory: claim coverage and controlled fixture responses

Base: `3cc5139b149feef390e6ceaa7358e2425d92620a` (PR131). This is an isolated
laboratory increment; no clinical content, source registry, last_checked,
prescribing, UI or operational model connection changes.

## Concrete risk and change

Phase3 can rank generic shared words as highly relevant and keeps every selected
candidate, including candidates with no specific content signal. In the observed
synthetic comparison, a generic assessment-only sentence scores1.0 in phase3.
Conversely the real authorized ACS assessment span scores0.0 against the declared
question because its wording does not repeat the question's disease name.

`rag_phase4.retrieve` reuses phase3's whole-index integrity, source permission,
version/date, graph joins, exact question IDs and contradiction gates. Then it:

1. Uses binary content-term features, excluding explicit generic stop words and
   generic concepts; repetitions cannot increase a score.
2. Adds only the already verified canonical module ID as semantic context. The
   join must have passed the existing pinned source/index/graph validator first.
3. Deduplicates citation identity and selects one relevant source per required
   curated claim. A missing claim, zero relevant signal, conflicting stance or
   excessive citation budget produces ABSTAIN. Duplicate high-score rows cannot
   crowd out another claim or inflate coverage.
4. Binds the selected ID to exact document, source hash, version, path, line range
   and text hash. Existing exact escaped quotes and provenance are preserved.

This does not introduce trained embeddings, general-language clinical relevance,
general contradiction inference or free patient queries. Existing semantic
concepts and curated stances retain their documented limits. Lexical-only mode
now abstains for the ACS assessment question when no specific body-content term
matches; hybrid mode can use its verified module context. Scores from different
rankers are not calibrated probabilities or clinical accuracy metrics.

The new reader is a library API over the existing graph/index:
`rag_phase4.retrieve(graph_path,index,synthetic_request,root=...)`.
The phase3 reader, its CLI and all old callers remain unchanged; no interface is
silently switched to this experiment.

## Controlled response preparation, without an LLM

`run_fixture_lab` is functional only for three fixed **invented nonclinical**
cases about colored geometric markers. They are test fixtures, not another
knowledge base, medical guidance or patient records.

The caller must explicitly allow a fixture response. Only the reviewed local
`FixtureProvider` class is accepted; a provider instance and its recorded response
can be injected for reproducible verification. Unreviewed callbacks, clinical
question IDs and external providers are rejected before invocation. There is no
network or provider transport implementation and no enabling configuration.

Provider output must exactly reproduce the requested citation objects, including
claim, locator, source/version/hash and quote, covering every requested claim
once. Missing/duplicate citations, unsupported prose, extra instructions/tool
calls, invented facts, wrong source metadata and oversized output are rejected
without echoing the rejected text. Output order is normalized to the trusted
request order. These checks prepare a contract for a future separately reviewed
adapter; they are not a fidelity evaluation of an actual LLM.

```powershell
python -B -X utf8 clinical/scripts/rag_phase4.py
# default: ABSTAIN, no fixture provider invocation
python -B -X utf8 clinical/scripts/rag_phase4.py --allow-fixture-response
# two validated invented marker quotes; actual_LLM_calls remains0
python -B -X utf8 clinical/scripts/rag_phase4.py --case contradiction --allow-fixture-response
# ABSTAIN before provider invocation
```

Every result retains generation_performed=false, clinical_generation_authorized=false,
network_used=false and actual_LLM_calls=0. A successful fixture operation records
one actual local fixture invocation and its measured local latency. Tokens,
remote latency and billed cost are not measured or invented. This is a trusted
local Python laboratory, not a sandbox against a malicious same-process program.

## Verification and custody

Emergency MCP was used first for the focal task/QA/project-state read: three
successful real stdio operations, without reinstalling servers or repeating MCP
tests. Worktree setup/instructions were read before canonical data.

Observed checks for this increment:

-20 new meaningful tests: coverage, generic-word rejection, duplicate resistance,
  all prior source gates, citation mutations, invalid outputs and provider gating.
-90 total RAG tests PASS:70 inherited regression tests plus20 new. No PR131 CI
  rerun is claimed.
-Eight closed hybrid questions exercised against the unchanged397-node/417-edge
  graph; three exact source citations verified, five expected abstentions.
-Lexical-only ACS abstention explicitly checked.
-Three nonclinical fixture cases: validated support, insufficient evidence and
  contradiction; actual model calls0.
-The generic-only example's candidate count falls from a phase3 ranking to zero.
  The ACS hybrid score changes from0.0 to0.34641 using verified module context.
  Neither observation is a percentage saving, clinical accuracy result or
  evidence of real-model performance.

Index, quotes and clinical query responses remain LOCAL_ONLY. Publishable
deliverables contain only code, tests, this documentation and metadata receipts
without raw clinical extracts. Source module files, graphs and registries are
reused, not regenerated or modified. No participants, labels, approvals or
independent medical adjudications are fabricated.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
