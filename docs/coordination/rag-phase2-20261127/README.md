# RAG phase 2: bounded clinical-module content, offline synthetic questions

Task: `F4-RAG-FHIR-HL7-PACS-AGENTES-G05`. Base/copy version:
`a3ae85412a868c105c64ca8b491e1cb3a1df065c` (PR129). The pre-existing catalog,
registry and 397-node/417-edge graph retain their historical `1f0fed8d731f65168ac338b5ddb18f451fccc6d6`
pin; no graph is regenerated. `CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE`.

## Functional increment

`clinical/scripts/rag_clinical_extracts.py` indexes actual own project clinical
text, rather than only bibliographic metadata. Three predeclared synthetic
questions retrieve recognition/evaluation excerpts from two canonical files:

| Own content | Authorized lines | Bibliographic association, not a content license |
| --- | --- | --- |
| `clinical/modules/cardiovascular.md` | 3–6 and 10–11 | acute-coronary-syndrome → src-b3266402 |
| `clinical/modules/renal-metabolic.md` | 185 | adrenal-crisis → src-72ea28f7 |

There are no copied ESC/Society guideline paragraphs, new clinical statements,
dose calculations, source review dates or clinical status promotions. Each quote
is labelled `project_clinical_synthesis_not_primary_evidence`, never an exact
quotation of the external bibliographic guideline. The unchanged GREEN field is
reported as bibliographic registry status; clinical validation remains pending.
Individual authorship is not invented. Attribution identifies the repository.

The owner phase-2 instruction authorizes local work with authorized existing
content. For these own canonical files the grant is limited to this laboratory's
indexing, retrieval, quotation and testing. It creates no new external/editorial
license, training grant, production permission or permission to publish the
generated corpus. The source catalog's `license_status: unknown` for the two
associated external guidelines is preserved. Their full texts are not admitted.

The existing R89 custody manifest was examined first: 13 documents, with explicit
custody/private-study/loan or other restricted terms; its rights reference says
local consultation does not establish AI ingestion permission. No blanket grant
was inferred from public access, a catalog identity, a GREEN status, or a
noncommercial/no-derivatives label. This review does not change those licenses.

## Binding, integrity and query policy

The sealed manifest `rag/clinical-extracts-laboratory.json` enumerates exact file
hashes, allowed span hashes, curated claim slots, versions and synthetic questions.
Its SHA is pinned in code. All source and span hashes mean UTF-8 **CRLF→LF
normalized canonical/Git source bytes**, not the raw Windows file hash.

For each clinical document the adapter reuses `rag_provenance_retrieval.retrieve`
to validate the module's registry identity, catalog record and graph source node /
SUPPORTED_BY edge. It additionally validates the pinned module-index file, exact
row, and LOCATED_IN edge. Citations carry the actual copy Git version, exact line
range, authorized span/file digests, catalog/relation JSON pointers and the
separate declared bibliographic version. A bibliographic association never grants
text rights over that external source.

Every query rereads the manifest, full source files, allowed spans and unchanged
snapshot inputs and rebuilds the expected index. Rehashing a poisoned payload,
changing a status/claim or adding text outside an allowed span cannot make it
trusted. A change even outside a permitted span invalidates the full-file pin.
Bounds: 128 KiB per source (the existing bundles are ~67/73 kB), 32 chunks,
512 KiB index, 2 KiB query, 240-character exact predeclared question, 6-line /
1600-character chunk. The source-size limit belongs to this separate adapter;
the previous content pipeline's limits are unchanged.

Questions are a closed synthetic benchmark, not a patient-note interface or
general clinical search. Unknown text, additional patient fields and prescribing
questions abstain without echoing input. Missing required claim slots abstain
(the pediatric-specific ACS question is intentionally insufficient).

`copy_state` current/historical/pending, source permission, bibliographic status
and clinical validity are different fields. Only current pinned copies with a
valid consumer revalidation window can be returned. Historical-only content,
pending content, elapsed consumer windows, copy-version mismatches and conflicting
curated claims abstain. Dates are consumer snapshot guards, **not** scientific
currency certifications, clinical review dates, legal expiries or `last_checked`.
The historical image-workflow role remains unchanged and is not promoted by this
adapter. The three clinical content chunks are current pinned repository copies;
historical/pending/stale/conflicting combinations are explicitly invented
nonclinical fixtures, never manufactured medical evidence.

Conflict detection compares all current records' manually curated claim-slot
values before selection. It does not infer semantic/scientific disagreement from
arbitrary language, resolve guideline differences, rank evidence quality or claim
to detect every contradiction. The two Cedar fixtures intentionally disagree on
an invented signal; the result is empty ABSTAIN, not a fabricated clinical answer.

Document content is untrusted data. There is no LLM, instruction interpreter,
tool execution, active URL/HTML renderer or network client. Quotes are reversible
HTML/Markdown escaped text; consumers must use a text-only viewer. Injection
robustness follows this architecture, source pins and revalidation, not a word
blacklist. `rag_generation_adapter.py` is a separate inactive boundary that refuses
even `enabled=True`; it has no provider implementation. JSON size/depth errors
produce static ABSTAIN rather than a traceback.

## Focal checks and operation

New tests: `clinical/tests/test_rag_clinical_extracts.py` (15). Existing RAG
regressions remain 13 metadata +16 content +9 workflow/deep-JSON =38; total focal
RAG discovery is53, with new and previous results reported separately. The
existing `clinical/qa/qa_runner.py` already discovers `clinical/tests/test_*.py`.
No shared workflow or global suite was changed or run for this increment.

```powershell
python -m unittest discover -s clinical/tests -p test_rag_*.py -v
python clinical/scripts/rag_clinical_extracts.py index --graph knowledge-graph/generated/project-graph.json --as-of 2026-11-27 --output knowledge-graph/generated/clinical-extract-index.LOCAL_ONLY.json
python clinical/scripts/rag_clinical_extracts.py retrieve --graph knowledge-graph/generated/project-graph.json --index knowledge-graph/generated/clinical-extract-index.LOCAL_ONLY.json --query rag/fixtures/clinical-extracts/query-acs.json
```

The tests create a tiny temporary structural graph fixture and change only its
temporary contract graph digest. They exercise the real decoder, file reads,
joins and CLI in a child process with a 5-second timeout, without requiring a
second generated project graph. The delivery receipt separately exercises all
8 questions against the actual unchanged graph. No global suite, Linux repetition,
clinical accuracy study, UI, live source service or provider test is claimed.

Code, tests, this document, sealed manifest and original synthetic fixtures may
be reviewed/published by the coordinating root. The generated index, raw
retrieval answers, chunks and extract-containing logs stay **LOCAL_ONLY**, outside
Drive/Gemini/publication. Sanitized receipts contain statuses/counts/hashes and
locators only. These generated-corpus flags do not change the repository's
general license or restrict original already-public source documents/code.
