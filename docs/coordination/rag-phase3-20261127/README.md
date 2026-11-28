# RAG phase 3 — bounded scientific-query laboratory

Base: `f32d211eed6a7baa7c42aadae583f6726e9e7e9b`. International scope;
no clinical source, formula, evidence status or `last_checked` is changed.
CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.

## Implemented

`clinical/scripts/rag_phase3.py` adds lexical, semantic-concept and hybrid ranking
to the phase2 authorized extracts. `SemanticEncoder` is a replaceable trusted-code
interface; the shipped `ConceptEncoder` uses an explicit versioned multilingual
dictionary. Hybrid score is 0.4 lexical cosine + 0.6 concept cosine, with stable
document/line tie-breaking. This is a small curated semantic representation,
**not a trained embedding model or general semantic search**. A trained encoder
would require a separate authorized/versioned implementation and evaluation.

The unchanged phase2 gate revalidates original bytes, permissions, versions,
graph/module/source joins and dates before any ranking. It selects all required
claims and rejects contradictory curated stances, insufficient, expired,
historical or pending content. Ranking cannot discard required claims or turn
an abstention into an answer. Contradiction detection remains curated same-key
stance comparison, not a general natural-language inference detector.

The request accepts only a predeclared synthetic question ID, date and ranking
mode. Free text, patient notes and caller-selected backends are rejected without
echo. Two owned project summaries remain distinct from primary clinical evidence.
The 8-question benchmark is not clinical validation or an independent cohort.

`clinical/scripts/rag_llm_boundary.py` provides interchangeable `messages` and
`input` request-shape adapters. They serialize an envelope in memory, segregating
untrusted evidence from fixed instructions, and return only its digest and a
planning receipt. They contain **no transport or provider callback**. Generation,
network and tools remain disabled even if `enabled=True`. No external SDK,
credentials, remote model, embedding service or prescribing capability is added.

Input accounting uses serialized UTF-8 bytes plus 128 as an explicit conservative
local proxy, not an actual tokenizer. Output caps, input caps and estimated cost
caps are checked before the disabled dispatch boundary. Rates are **synthetic
fixture rates**, not quotations from a vendor. Provider tokens, billing and
latency remain `null`; a latency budget is recorded but no transport timeout is
claimed. Real retrieval latency is measured separately and includes source/graph
integrity checks. A connected provider and cumulative operational budgets remain
future work requiring their own authorization/security review.

`rag_phase3.py ui` generates a **viewer of synthetic-query results** with 8 native HTML
`details` controls, status/reason, citations, version and source line locators.
It has no JS, form, active source links, patient input or network requests; CSP
is `default-src 'none'; base-uri 'none'; form-action 'none'`. It is an independent
laboratory page, not an application feature or deployment. Results are computed
once when the CLI generates the file; expanding a panel does not run another
query. The separate `retrieve` CLI actually executes the hybrid retrieval for a
closed question ID. There is no free-query web interface. It contains authorized
quotes and must remain **LOCAL_ONLY** alongside the index and raw query outputs.
Static contract tests do not constitute a browser visual or accessibility pass.

## Local commands

With the existing verified graph and phase2 index inside the operator's CLI root:

```text
python clinical/scripts/rag_phase3.py retrieve --graph knowledge-graph/generated/project-graph.json --index knowledge-graph/generated/phase3-LOCAL_ONLY/index.json --query knowledge-graph/generated/phase3-LOCAL_ONLY/query.json
python clinical/scripts/rag_phase3.py ui --graph knowledge-graph/generated/project-graph.json --index knowledge-graph/generated/phase3-LOCAL_ONLY/index.json --as-of 2026-11-27 --output knowledge-graph/generated/phase3-LOCAL_ONLY/scientific-query.LOCAL_ONLY.html
python -m unittest discover -s clinical/tests -p test_rag_phase3.py
```

Example query (synthetic metadata only):

```json
{"synthetic":true,"question_id":"acs-exclusion","as_of":"2026-11-27","mode":"hybrid"}
```

Tests are in the existing `clinical/tests` discovery path. Verification covers
cross-language concepts with zero lexical overlap, deterministic hybrid ranking,
exact citation fidelity and graph joins, conflict/staleness/insufficiency gates,
forged indexes, free patient fields, unknown providers, budget limits, inert
document commands, static UI and the actual CLI parsing/output path.

Publish only code, this document, patch and quote-free verification metadata.
Do not publish generated index, quotes, raw retrieval results or the HTML page.
No visual PASS, broad clinical relevance, absence of bias or provider security
assessment is inferred from these tests. Main, protected branches, ZIPs,
19 contracts, 45 formulas and prior medical decisions remain untouched.
