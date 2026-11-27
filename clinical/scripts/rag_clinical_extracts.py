#!/usr/bin/env python3
"""Offline, bounded clinical-module extracts for predeclared synthetic questions.

Own project synthesis is not a quotation from its bibliographic guideline. No
provider, instruction interpreter, patient input, prescription or network path.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cli_paths import input_file, output_file
from rag_content_retrieval import MAX_CHUNK_CHARS, canonical_bytes, inert_quote, _chunks, _date
from rag_provenance_retrieval import ROOT, TASK_ID, load_snapshot, retrieve, sha256

COPY_COMMIT = "a3ae85412a868c105c64ca8b491e1cb3a1df065c"
MANIFEST_PATH = "rag/clinical-extracts-laboratory.json"
MANIFEST_SHA256 = "ebb620b9409f4d8cef1054b8f7569004a42401c727753b581189981163aad568"
INDEX_PATH = "clinical/references/module-index.md"
INDEX_SHA256 = "1e06e639bb7e89487b4ac6dfbdc4ea534ef1f2cf59f161eb75f937657ac52301"
MAX_DOCUMENT_BYTES = 131072
MAX_INDEX_BYTES = 524288


class ClinicalExtractRejected(ValueError):
    """Static refusal; no source text, path diagnostics or caller text."""


def _read_lf(root, relative, limit):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ClinicalExtractRejected("CLINICAL_SOURCE_UNAVAILABLE")
    if path.stat().st_size > limit:
        raise ClinicalExtractRejected("CLINICAL_SOURCE_SIZE_LIMIT")
    return path.read_bytes().replace(b"\r\n", b"\n")


def load_manifest(root=ROOT):
    raw = _read_lf(root, MANIFEST_PATH, 32768)
    if sha256(raw) != MANIFEST_SHA256:
        raise ClinicalExtractRejected("CLINICAL_PERMISSION_OR_POLICY_INTEGRITY_MISMATCH")
    return json.loads(raw)


def _binding(snapshot, item, root):
    """Reuse the catalog/registry/source-node/SUPPORTED_BY metadata validator."""
    query = {"synthetic": True, "module_id": item["module_id"],
             "source_id": item["bibliographic_source_id"],
             "expected_version": item["declared_bibliographic_version"]}
    resolved = retrieve(snapshot, query)
    if resolved["status"] != "RETRIEVED_METADATA":
        raise ClinicalExtractRejected("CLINICAL_DOCUMENT_MODULE_SOURCE_JOIN_MISMATCH")
    raw = _read_lf(root, INDEX_PATH, MAX_DOCUMENT_BYTES)
    literal = "| " + item["module_id"] + " | `" + item["path"].removeprefix("clinical/") + "` |"
    if sha256(raw) != INDEX_SHA256 or raw.decode("utf-8").splitlines()[item["module_index_line"] - 1] != literal:
        raise ClinicalExtractRejected("CLINICAL_MODULE_FILE_JOIN_MISMATCH")
    edge = {"source": "module:" + item["module_id"],
            "target": "bundle:" + item["path"].removeprefix("clinical/"), "type": "LOCATED_IN"}
    if edge not in snapshot["graph"]["edges"]:
        raise ClinicalExtractRejected("CLINICAL_GRAPH_FILE_JOIN_MISMATCH")
    citation = resolved["citations"][0]
    return {"module_id": item["module_id"], "bibliographic_source_id": item["bibliographic_source_id"],
            "declared_bibliographic_version": item["declared_bibliographic_version"],
            "bibliographic_role": citation["role"], "evidence_status_unchanged": citation["evidence_status_unchanged"],
            "catalog_json_pointer": citation["catalog_json_pointer"],
            "module_relation_json_pointer": citation["module_relation_json_pointer"],
            "module_index_path": INDEX_PATH, "module_index_line": item["module_index_line"],
            "module_index_sha256": INDEX_SHA256,
            "external_guideline_text_indexed": False, "external_guideline_rights_granted": False}


def _sections(item, root):
    raw = _read_lf(root, item["path"], MAX_DOCUMENT_BYTES)
    if sha256(raw) != item["sha256"]:
        raise ClinicalExtractRejected("CLINICAL_SOURCE_INTEGRITY_MISMATCH")
    lines = raw.decode("utf-8").splitlines(keepends=True)
    for span in item["spans"]:
        text = "".join(lines[span["start"] - 1:span["end"]])
        if (sha256(text.encode("utf-8")) != span["sha256"] or len(text) > 6400
                or any(len(line) > MAX_CHUNK_CHARS for line in text.splitlines())):
            raise ClinicalExtractRejected("CLINICAL_AUTHORIZED_SPAN_MISMATCH")
        yield text, span


def _document_rows(snapshot, item, root):
    binding = _binding(snapshot, item, root) if item["source_class"] == "project_clinical_synthesis" else {}
    rows = []
    for text, span in _sections(item, root):
        for chunk in _chunks(text):
            rows.append({"document_id": item["document_id"], "source_class": item["source_class"],
                         "path": item["path"], "version": item["version"], "source_sha256": item["sha256"],
                         "source_hash_mode": "utf8_lf_normalized_git_source_bytes",
                         "copy_state": item["copy_state"], "valid_through": item["valid_through"],
                         "authorized_span_start": span["start"], "authorized_span_end": span["end"],
                         "authorized_span_sha256": span["sha256"], "topic": span["topic"],
                         "claim_key": span["claim_key"], "stance": span["stance"], **chunk,
                         "line_start": chunk["line_start"] + span["start"] - 1,
                         "line_end": chunk["line_end"] + span["start"] - 1, **binding})
    return rows


def build_index(graph_path, as_of, *, root=ROOT):
    manifest = load_manifest(root)
    evaluated = _date(as_of)
    if not _date(manifest["snapshot_date"]) <= evaluated <= _date(manifest["revalidate_after"]):
        raise ClinicalExtractRejected("CLINICAL_SNAPSHOT_REVALIDATION_REQUIRED")
    snapshot = load_snapshot(graph_path, root=root)
    rows = [row for item in manifest["documents"] for row in _document_rows(snapshot, item, root)]
    if len(rows) > 32:
        raise ClinicalExtractRejected("CLINICAL_INDEX_CHUNK_LIMIT")
    return {"schema": "emergency-clinical-extract-index-v1", "built_for_date": as_of,
            "manifest_sha256": MANIFEST_SHA256, "snapshot_sha256": snapshot["hashes"],
            "source_commit": COPY_COMMIT, "chunks": rows,
            "clinical_use_authorized": False, "generated_corpus_scope": "LOCAL_ONLY"}


def _question(manifest, query):
    allowed = {"synthetic", "question", "as_of", "expected_version"}
    if not isinstance(query, dict) or set(query) - allowed or query.get("synthetic") is not True:
        raise ClinicalExtractRejected("PREDECLARED_SYNTHETIC_QUESTION_REQUIRED")
    text = query.get("question")
    if not isinstance(text, str) or len(text) > 240:
        raise ClinicalExtractRejected("PREDECLARED_SYNTHETIC_QUESTION_REQUIRED")
    found = [item for item in manifest["questions"] if item["question"] == text]
    if len(found) != 1:
        raise ClinicalExtractRejected("QUESTION_OUTSIDE_AUTHORIZED_SYNTHETIC_SCOPE")
    if query.get("expected_version", "git:" + COPY_COMMIT) != "git:" + COPY_COMMIT:
        raise ClinicalExtractRejected("CLINICAL_COPY_VERSION_MISMATCH")
    return found[0]


def _validate_index(graph_path, manifest, index, query, root):
    if not isinstance(index, dict) or index.get("schema") != "emergency-clinical-extract-index-v1":
        raise ClinicalExtractRejected("INVALID_CLINICAL_CONTENT_INDEX")
    evaluated = _date(query.get("as_of"))
    if not _date(index.get("built_for_date")) <= evaluated <= _date(manifest["revalidate_after"]):
        raise ClinicalExtractRejected("CLINICAL_INDEX_STALE_OR_DATE_INVALID")
    # Re-read the pinned manifest, source files/spans and graph/catalog/registry.
    # Index text, rehashed payloads, statuses and semantic annotations are untrusted.
    expected = build_index(graph_path, index["built_for_date"], root=root)
    if canonical_bytes(index) != canonical_bytes(expected):
        raise ClinicalExtractRejected("CLINICAL_INDEX_CONTENT_OR_BINDING_MISMATCH")
    return evaluated


def _current_rows(rows, evaluated):
    if not rows:
        raise ClinicalExtractRejected("INSUFFICIENT_AUTHORIZED_CONTENT")
    if any(row["copy_state"] == "pending" for row in rows):
        raise ClinicalExtractRejected("CONTENT_PENDING_RECONCILIATION")
    current = [row for row in rows if row["copy_state"] == "current"]
    if not current:
        raise ClinicalExtractRejected("HISTORICAL_CONTENT_NOT_CURRENT_EVIDENCE")
    if any(evaluated > _date(row["valid_through"]) for row in current):
        raise ClinicalExtractRejected("CONTENT_REVALIDATION_REQUIRED")
    return current


def _select(index, question, evaluated):
    rows = [row for row in index["chunks"] if row["topic"] == question["topic"]]
    current = _current_rows(rows, evaluated)
    claims = {}
    for row in current:
        claims.setdefault(row["claim_key"], set()).add(row["stance"])
    if any(len(stances) > 1 for stances in claims.values()):
        raise ClinicalExtractRejected("CONTRADICTORY_CURATED_CLAIMS_REQUIRE_REVIEW")
    if not set(question["required_claims"]) <= set(claims):
        raise ClinicalExtractRejected("INSUFFICIENT_AUTHORIZED_CONTENT")
    return [row for row in current if row["claim_key"] in question["required_claims"]]


def _citation(row):
    citation = {key: value for key, value in row.items() if key not in {"text", "topic", "stance", "claim_key"}}
    own = row["source_class"] == "project_clinical_synthesis"
    citation.update(quote=inert_quote(row["text"]), quote_encoding="html-and-markdown-escaped-untrusted-text",
                    source_commit=COPY_COMMIT if own else None,
                    scope="project_clinical_synthesis_not_primary_evidence" if own else "invented_nonclinical_conflict_fixture",
                    source_attribution="Emergency repository canonical module" if own else "Emergency laboratory fixture",
                    clinical_primary_evidence=False, clinical_validation_state="CLINICALLY_PENDING")
    return citation


def _result(reason=None, citations=None):
    citations = citations or []
    return {"schema": "emergency-clinical-extract-result-v1", "task_id": TASK_ID,
            "status": "ABSTAIN" if reason else "EXTRACTIVE_CONTENT", "reason": reason,
            "answer_mode": "escaped_extracts_only_no_model", "citations": citations,
            "answer": "\n\n".join(item["quote"] for item in citations),
            "generation_performed": False, "document_text_is_untrusted_data": True,
            "synthetic_benchmark_only": True, "real_patient_question_supported": False,
            "external_clinical_evidence_ingested": False,
            "tools_or_urls_activated": False, "clinical_primary_evidence": False,
            "prescribing_authorized": False, "runtime_activation_authorized": False,
            "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}


def retrieve_extracts(graph_path, index, query, *, root=ROOT):
    try:
        manifest = load_manifest(root)
        question = _question(manifest, query)
        evaluated = _validate_index(graph_path, manifest, index, query, root)
        citations = [_citation(row) for row in _select(index, question, evaluated)]
        result = _result(citations=citations)
        result.update(question_id=question["id"], index_sha256=sha256(canonical_bytes(index)),
                      snapshot_sha256=index["snapshot_sha256"], corpus_scope="LOCAL_ONLY")
        return result
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        return _result(str(error) if isinstance(error, ClinicalExtractRejected) else "INVALID_OR_UNAVAILABLE_CLINICAL_INPUT")


def main(argv=None, *, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("index", "retrieve"):
        command = sub.add_parser(name)
        command.add_argument("--graph", required=True, type=input_file)
        if name == "index":
            command.add_argument("--as-of", required=True)
            command.add_argument("--output", required=True, type=output_file)
        else:
            command.add_argument("--index", required=True, type=input_file)
            command.add_argument("--query", required=True, type=input_file)
    args = parser.parse_args(argv)
    try:
        if args.operation == "index":
            index = build_index(args.graph, args.as_of, root=root)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(index, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
            result = {"status": "INDEXED", "chunks": len(index["chunks"]),
                      "index_sha256": sha256(canonical_bytes(index)), "corpus_scope": "LOCAL_ONLY"}
        else:
            if args.index.stat().st_size > MAX_INDEX_BYTES or args.query.stat().st_size > 2048:
                raise ClinicalExtractRejected("CLINICAL_INDEX_OR_QUERY_SIZE_LIMIT")
            result = retrieve_extracts(args.graph, json.loads(args.index.read_text(encoding="utf-8")),
                                       json.loads(args.query.read_text(encoding="utf-8")), root=root)
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        result = _result(str(error) if isinstance(error, ClinicalExtractRejected) else "INVALID_OR_UNAVAILABLE_CLINICAL_INPUT")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "ABSTAIN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
