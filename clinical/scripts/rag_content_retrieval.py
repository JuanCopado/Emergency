#!/usr/bin/env python3
"""Local extractive content retrieval: authorized own governance and separate fixtures.

Document text is data, never instructions. There is no model, tool execution,
network client, HTML renderer or clinical decision path in this module.
"""
from __future__ import annotations

import argparse
from datetime import date
import html
import json
from pathlib import Path
import re

from cli_paths import input_file, output_file
from rag_provenance_retrieval import ROOT, SOURCE_COMMIT, TASK_ID, load_snapshot, sha256
import rag_canonical_workflow as workflow

MANIFEST_PATH = "rag/content-laboratory.json"
MAX_SOURCE_BYTES = 65536
MAX_INDEX_BYTES = 524288
MAX_CHUNK_CHARS = 1600
USES = ["local_indexing", "local_retrieval", "local_quotation", "local_testing"]
OWN = {
    "docs/INTERNATIONAL_SCOPE.md": ("own-international-scope", "fc3885c867c98cc682d9c14b62099df32db2f74a8b2f28c4a8e4480ae29e173b"),
    "docs/coordination/r5-g05-20261126/G05_REQUISITOS.json": ("own-g05-requirements", "c5ab01649e1df9c8c9d7948f632e62f80b3adcbcde2807c21386cc7e37a68e2d"),
}
# Additional quarantine only. The security boundary is no instruction interpreter,
# no tools/model/network, pinned source bytes and revalidation of every query.
OVERRIDE_MARKERS = re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions|\bSYSTEM\s*:|<\|im_start\|>|<script\b|\bcall_tool\b", re.I)


class ContentRejected(ValueError):
    """A static code, without source content or caller text."""


def canonical_bytes(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def _date(value):
    try:
        if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise ValueError
        return date.fromisoformat(value)
    except ValueError:
        raise ContentRejected("INVALID_EVALUATION_DATE") from None


def load_manifest(root=ROOT):
    raw = (root / MANIFEST_PATH).read_bytes()
    if len(raw) > MAX_SOURCE_BYTES:
        raise ContentRejected("MANIFEST_TOO_LARGE")
    manifest = json.loads(raw)
    if not isinstance(manifest, dict):
        raise ContentRejected("INVALID_CONTENT_MANIFEST")
    expected = {"schema": "emergency-rag-content-laboratory-v1", "task_id": TASK_ID,
                "scope": "own_governance_bound_internal_workflow_and_separate_synthetic_fixtures_only",
                "authority": "owner_instruction_for_this_local_laboratory_2026-11-27",
                "source_commit": SOURCE_COMMIT, "allowed_uses": USES,
                "restriction_scope": "generated_rag_corpus_and_consumption_not_original_source_or_code_publication",
                "redistribution_authorized": False, "training_authorized": False,
                "external_processing_authorized": False, "clinical_use_authorized": False}
    if any(type(manifest.get(k)) is not type(v) or manifest.get(k) != v for k, v in expected.items()):
        raise ContentRejected("CONTENT_PERMISSION_SCOPE_MISMATCH")
    documents = manifest.get("documents")
    if (not isinstance(documents, list) or not 1 <= len(documents) <= 12
            or any(not isinstance(item, dict) for item in documents)):
        raise ContentRejected("INVALID_CONTENT_MANIFEST")
    ids = [item.get("source_id") for item in documents]
    if (any(not isinstance(value, str) or re.fullmatch(r"[a-z0-9-]{1,100}", value) is None for value in ids)
            or len(set(ids)) != len(ids)):
        raise ContentRejected("DUPLICATE_CONTENT_SOURCE")
    return manifest


def _workflow_audit(snapshot, manifest, root):
    items = [item for item in manifest["documents"] if item.get("source_id") == workflow.SOURCE_ID]
    if len(items) != 1:
        raise ContentRejected("CANONICAL_WORKFLOW_NOT_AUTHORIZED")
    item = items[0]
    text = _document(item, root)
    binding = workflow.validate_binding(snapshot, root)
    workflow.sections(text, binding)
    return binding


def canonical_content_audit(snapshot, manifest=None, *, root=ROOT):
    """A verified license label alone is not a field/use content permission."""
    graph_ids = {node["id"] for node in snapshot["graph"]["nodes"]}
    manifest = load_manifest(root) if manifest is None else manifest
    return [_audit_source(source, snapshot, manifest, root, graph_ids) for source in snapshot["catalog"]["sources"]]


def _audit_source(source, snapshot, manifest, root, graph_ids):
    reason = "SOURCE_CONTENT_USE_NOT_CLEARED_FOR_THIS_LAB_SCOPE"
    if source["source_id"] == workflow.SOURCE_ID:
        try:
            binding = _workflow_audit(snapshot, manifest, root)
            return {"source_id": source["source_id"], "license_status_unchanged": source.get("license_status"),
                    "content_status": "AUTHORIZED_LOCAL_WORKFLOW_SPANS", "reasons": [], **binding}
        except (workflow.WorkflowRejected, ContentRejected, OSError) as error:
            reason = str(error) if isinstance(error, ValueError) else "CANONICAL_WORKFLOW_UNAVAILABLE"
    reasons = [reason]
    if source.get("compound_identity"):
        reasons.append("COMPOUND_IDENTITY_UNRESOLVED")
    if not source.get("version"):
        reasons.append("CONTENT_VERSION_UNRESOLVED")
    if "source:" + source["source_id"] not in graph_ids:
        reasons.append("GRAPH_SOURCE_MISSING")
    return {"source_id": source["source_id"], "license_status_unchanged": source.get("license_status"),
            "content_status": "BLOCKED", "reasons": reasons}


def _check_permission(item):
    relative = item.get("path", "")
    version = item.get("version")
    grant = item.get("permission", {})
    if (not isinstance(relative, str) or not isinstance(grant, dict)
            or not isinstance(version, str) or not 1 <= len(version) <= 96
            or grant.get("status") != "explicit_owner_local_laboratory_permission"
            or grant.get("allowed_uses") != USES or grant.get("authorized_version") != version
            or grant.get("authorized_sha256") != item.get("sha256")
            or grant.get("restriction_scope") != "generated_rag_corpus_and_consumption_only"
            or grant.get("redistribution") is not False or grant.get("training") is not False
            or grant.get("clinical_use") is not False):
        raise ContentRejected("SOURCE_PERMISSION_OR_VERSION_MISMATCH")


def _source_class_guard(item):
    source_class, relative, version = item["source_class"], item["path"], item["version"]
    if source_class == "project_governance":
        if relative not in OWN or (item.get("source_id"), item.get("sha256")) != OWN[relative] or version != "git:" + SOURCE_COMMIT:
            raise ContentRejected("OWN_SOURCE_NOT_PINNED_TO_AUTHORIZED_VERSION")
    elif source_class == "synthetic_fixture":
        if not relative.startswith("rag/fixtures/content/") or not str(item.get("source_id", "")).startswith("fixture-"):
            raise ContentRejected("FIXTURE_SOURCE_NOT_SEPARATE")
    elif source_class == "project_owned_workflow":
        try:
            workflow.validate_identity(item)
        except workflow.WorkflowRejected as error:
            raise ContentRejected(str(error)) from None
    else:
        raise ContentRejected("SOURCE_CLASS_NOT_AUTHORIZED")


def _source_path(item, root):
    _source_class_guard(item)
    source_class, relative = item["source_class"], item["path"]
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ContentRejected("SOURCE_PATH_NOT_PERMITTED")
    if source_class == "synthetic_fixture" and not target.is_relative_to((root / "rag/fixtures/content").resolve()):
        raise ContentRejected("FIXTURE_SOURCE_NOT_SEPARATE")
    return target


def _document(item, root):
    _check_permission(item)
    target = _source_path(item, root)
    if target.stat().st_size > MAX_SOURCE_BYTES:
        raise ContentRejected("SOURCE_TOO_LARGE")
    raw = target.read_bytes().replace(b"\r\n", b"\n")
    if sha256(raw) != item.get("sha256"):
        raise ContentRejected("SOURCE_INTEGRITY_MISMATCH")
    text = raw.decode("utf-8")
    if any(len(line) > MAX_CHUNK_CHARS for line in text.splitlines()):
        raise ContentRejected("SOURCE_LINE_TOO_LARGE")
    return text


def _chunks(text):
    lines = text.splitlines()
    group, start, chars = [], 0, 0
    for number, line in enumerate(lines, 1):
        if not line.strip() or len(group) == 6 or chars + len(line) + 1 > MAX_CHUNK_CHARS:
            if group:
                yield {"line_start": start, "line_end": start + len(group) - 1, "text": "\n".join(group)}
            group, chars = [], 0
        if line.strip():
            if not group:
                start = number
            group.append(line)
            chars += len(line) + 1
    if group:
        yield {"line_start": start, "line_end": start + len(group) - 1, "text": "\n".join(group)}


def _index_section(item, section):
    text, offset, binding = section
    if OVERRIDE_MARKERS.search(text):
        raise ContentRejected("DOCUMENT_OVERRIDE_MARKERS_QUARANTINED")
    return [{"source_id": item["source_id"], "source_class": item["source_class"],
             "version": item["version"], "path": item["path"], "source_sha256": item["sha256"],
             "source_hash_mode": "utf8_lf_normalized", **chunk,
             "line_start": chunk["line_start"] + offset, "line_end": chunk["line_end"] + offset,
             **binding} for chunk in _chunks(text)]


def _index_document(item, root, evaluated, snapshot):
    text = _document(item, root)
    expiry = item.get("fixture_valid_through")
    if expiry is not None and evaluated > _date(expiry):
        raise ContentRejected("SOURCE_STALE")
    sections = [(text, 0, {})]
    if item["source_class"] == "project_owned_workflow":
        try:
            sections = workflow.sections(text, workflow.validate_binding(snapshot, root))
        except workflow.WorkflowRejected as error:
            raise ContentRejected(str(error)) from None
    return [chunk for section in sections for chunk in _index_section(item, section)]


def build_index(snapshot, manifest, as_of, *, root=ROOT):
    evaluated = _date(as_of)
    if not _date(manifest["snapshot_date"]) <= evaluated <= _date(manifest["revalidate_after"]):
        raise ContentRejected("SNAPSHOT_REVALIDATION_REQUIRED")
    rows, excluded = [], []
    for item in manifest["documents"]:
        # A single poisoned/unauthorized source is an explicit per-source block.
        try:
            rows.extend(_index_document(item, root, evaluated, snapshot))
        except ContentRejected as error:
            excluded.append({"source_id": item["source_id"], "reason": str(error)})
    if len(rows) > 256:
        raise ContentRejected("INDEX_CHUNK_LIMIT")
    return {"schema": "emergency-rag-content-index-v1", "built_for_date": as_of,
            "revalidate_after": manifest["revalidate_after"], "manifest_sha256": sha256(canonical_bytes(manifest)),
            "snapshot_sha256": snapshot["hashes"], "chunks": rows, "excluded": excluded,
            "clinical_use_authorized": False}


def _tokens(text):
    return re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)


def inert_quote(text):
    value = html.escape(text, quote=True)
    # Preserve an exact reversible quote while neutralizing Markdown links and
    # URI schemes as well as HTML. Consumers must still use a text-only viewer.
    for character in "[]()`:":
        value = value.replace(character, "&#" + str(ord(character)) + ";")
    return value


def _result(reason=None, citations=None):
    citations = citations or []
    return {"schema": "emergency-rag-content-result-v1", "task_id": TASK_ID,
            "status": "ABSTAIN" if reason else "EXTRACTIVE_CONTENT",
            "reason": reason, "answer_mode": "escaped_extracts_only_no_model",
            "answer": "\n\n".join("[" + str(i) + "] " + item["quote"] for i, item in enumerate(citations, 1)),
            "citations": citations, "document_text_is_untrusted_data": True,
            "tools_or_urls_activated": False, "clinical_primary_evidence": False,
            "prescribing_authorized": False, "runtime_activation_authorized": False,
            "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}


def _query_error(snapshot, manifest, query):
    allowed = {"synthetic", "text", "source_id", "expected_version", "as_of", "top_k"}
    if (not isinstance(query, dict) or set(query) - allowed or query.get("synthetic") is not True
            or not isinstance(query.get("text"), str) or not 1 <= len(query["text"]) <= 160
            or re.fullmatch(r"[^\W\d_]+(?: +[^\W\d_]+)*", query["text"], flags=re.UNICODE) is None
            or type(query.get("top_k", 2)) is not int or not 1 <= query.get("top_k", 2) <= 3):
        return "SYNTHETIC_LAB_QUERY_REQUIRED"
    tokens = set(_tokens(query["text"]))
    if not tokens or not tokens <= set(manifest["allowed_query_tokens"]):
        return "QUERY_OUTSIDE_SYNTHETIC_LAB_VOCABULARY"
    source_id = query.get("source_id")
    if source_id is not None and (not isinstance(source_id, str) or re.fullmatch(r"[a-z0-9-]{1,100}", source_id) is None):
        return "SOURCE_NOT_AUTHORIZED"
    version = query.get("expected_version")
    if version is not None and (not isinstance(version, str) or not 1 <= len(version) <= 96):
        return "CONTENT_VERSION_MISMATCH"
    if source_id != workflow.SOURCE_ID and source_id in {source["source_id"] for source in snapshot["catalog"]["sources"]}:
        return "CANONICAL_SOURCE_CONTENT_NOT_AUTHORIZED"
    return None


def _index_error(snapshot, manifest, index, query, root):
    if not isinstance(index, dict) or index.get("schema") != "emergency-rag-content-index-v1":
        return "INVALID_CONTENT_INDEX"
    try:
        evaluated = _date(query.get("as_of"))
        built_for = _date(index.get("built_for_date"))
    except ContentRejected:
        return "INVALID_EVALUATION_DATE"
    if not built_for <= evaluated <= _date(manifest["revalidate_after"]):
        return "STALE_INDEX_OR_EVALUATION_DATE"
    # Re-read authorized source files, permissions and hashes on every query.
    # Never trust text, version, spans, bindings or exclusions stored in an index.
    expected = build_index(snapshot, manifest, index["built_for_date"], root=root)
    if canonical_bytes(index) != canonical_bytes(expected):
        return "INDEX_CONTENT_OR_BINDING_MISMATCH"
    return None


def _source_eligibility(manifest, index, query):
    source_id, evaluated = query.get("source_id"), _date(query["as_of"])
    if source_id is not None and source_id not in {item["source_id"] for item in manifest["documents"]}:
        return "SOURCE_NOT_AUTHORIZED", set()
    for blocked in index["excluded"]:
        if blocked["source_id"] == source_id:
            return blocked["reason"], set()
    expired = {item["source_id"] for item in manifest["documents"]
               if item.get("fixture_valid_through") is not None and evaluated > _date(item["fixture_valid_through"])}
    if source_id in expired:
        return "SOURCE_STALE", expired
    return None, expired


def _rank_matches(index, query, expired):
    source_id, tokens = query.get("source_id"), set(_tokens(query["text"]))
    rows = [row for row in index["chunks"] if row["source_id"] not in expired
            and (source_id is None or row["source_id"] == source_id)]
    if query.get("expected_version") is not None:
        rows = [row for row in rows if row["version"] == query["expected_version"]]
        if not rows:
            return [], "CONTENT_VERSION_MISMATCH"
    matches = [(sum(_tokens(row["text"]).count(token) for token in tokens), row) for row in rows
               if tokens <= set(_tokens(row["text"]))]
    matches.sort(key=lambda item: (-item[0], item[1]["source_id"], item[1]["line_start"]))
    return matches, None


def _citation(row):
    citation = {key: row[key] for key in ("source_id", "source_class", "version", "path", "source_sha256", "source_hash_mode", "line_start", "line_end")}
    own = row["source_class"] in {"project_governance", "project_owned_workflow"}
    scopes = {"project_governance": "governance_not_primary_clinical_evidence",
              "project_owned_workflow": "internal_workflow_not_primary_evidence"}
    citation.update(quote=inert_quote(row["text"]), quote_encoding="html-and-markdown-escaped-untrusted-text",
                    source_commit=SOURCE_COMMIT if own else None,
                    scope=scopes.get(row["source_class"], "invented_nonclinical_fixture"))
    if row["source_class"] == "project_owned_workflow":
        citation.update({key: row[key] for key in workflow.CITATION_FIELDS})
    return citation


def retrieve_content(snapshot, manifest, index, query, *, root=ROOT):
    reason = _query_error(snapshot, manifest, query)
    if reason:
        return _result(reason)
    reason = _index_error(snapshot, manifest, index, query, root)
    if reason:
        return _result(reason)
    reason, expired = _source_eligibility(manifest, index, query)
    if reason:
        return _result(reason)
    matches, reason = _rank_matches(index, query, expired)
    if reason:
        return _result(reason)
    citations = [_citation(row) for _, row in matches[:query.get("top_k", 2)]]
    result = _result(None if citations else "NO_AUTHORIZED_MATCH", citations)
    result.update(index_sha256=sha256(canonical_bytes(index)), snapshot_sha256=snapshot["hashes"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("index", "retrieve", "audit-rights"):
        command = sub.add_parser(name)
        command.add_argument("--graph", required=True, type=input_file)
        if name == "index":
            command.add_argument("--as-of", required=True)
            command.add_argument("--output", required=True, type=output_file)
        elif name == "retrieve":
            command.add_argument("--index", required=True, type=input_file)
            command.add_argument("--query", required=True, type=input_file)
    args = parser.parse_args(argv)
    try:
        snapshot = load_snapshot(args.graph)
        manifest = load_manifest()
        if args.operation == "audit-rights":
            result = {"status": "CONTENT_RIGHTS_AUDIT", "canonical_sources": canonical_content_audit(snapshot),
                      "own_governance_authorized_paths": sorted(OWN), "scope": manifest["scope"]}
        elif args.operation == "index":
            index = build_index(snapshot, manifest, args.as_of)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(index, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
            result = {"status": "INDEXED", "chunks": len(index["chunks"]), "excluded": index["excluded"],
                      "index_sha256": sha256(canonical_bytes(index)), "clinical_use_authorized": False}
        else:
            if args.index.stat().st_size > MAX_INDEX_BYTES or args.query.stat().st_size > 2048:
                raise ContentRejected("INDEX_OR_QUERY_SIZE_LIMIT")
            result = retrieve_content(snapshot, manifest, json.loads(args.index.read_text(encoding="utf-8")),
                                      json.loads(args.query.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        result = _result(str(error) if isinstance(error, ContentRejected) else "INVALID_OR_UNAVAILABLE_CONTENT_INPUT")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "ABSTAIN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
