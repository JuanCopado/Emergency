#!/usr/bin/env python3
"""Offline retrieval of cited catalog metadata for the synthetic RAG prototype.

This first retrieval stage never reads source documents or patient questions,
calls a provider, generates clinical advice, or changes evidence states.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from cli_paths import input_file

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = "clinical/references/evidence-sources.json"
REGISTRY_PATH = "clinical/references/evidence-registry.json"
CONTRACT_PATH = "rag/synthetic-provenance-consumer.json"
TASK_ID = "F4-RAG-FHIR-HL7-PACS-AGENTES-G05"
SOURCE_COMMIT = "1f0fed8d731f65168ac338b5ddb18f451fccc6d6"
FIELDS = ("source_id", "title", "organization", "source_type", "url", "persistent_id",
          "version", "publication_date", "last_verified", "language", "jurisdiction",
          "license_status", "compound_identity")
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class SnapshotRejected(ValueError):
    """Static reason only: never attach input documents or file contents."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def _validate_contract(contract):
    expected = {
        "schema": "emergency-synthetic-provenance-consumer-v1",
        "task_id": TASK_ID,
        "consumer": "offline-synthetic-provenance-cli",
        "synthetic_only": True,
        "allowed_metadata_fields": list(FIELDS),
        "licensed_source_content_fields": [],
        "external_consumers_enabled": False,
        "clinical_generation_enabled": False,
        "production_rights_granted": False,
        "G05_closed": [],
        "clinical": "CLINICALLY_PENDING",
        "release": "NO_GO_CLINICAL_RELEASE",
    }
    if any(type(contract.get(key)) is not type(value) or contract.get(key) != value
           for key, value in expected.items()):
        raise SnapshotRejected("CONSUMER_SCOPE_NOT_AUTHORIZED")
    if contract.get("source_commit") != SOURCE_COMMIT:
        raise SnapshotRejected("SOURCE_COMMIT_NOT_PINNED")


def load_snapshot(graph_path, *, root=ROOT):
    """Read the existing graph and canonical files; never generate another graph."""
    contract_bytes = (root / CONTRACT_PATH).read_bytes()
    contract = json.loads(contract_bytes)
    _validate_contract(contract)
    paths = {"catalog": root / CATALOG_PATH, "registry": root / REGISTRY_PATH,
             "graph": Path(graph_path)}
    documents, hashes = {}, {}
    for name, path in paths.items():
        raw = path.read_bytes()
        # These two Git text files may use CRLF in a Windows checkout. Compare
        # their canonical Git LF bytes; the separately supplied graph stays exact.
        if name in {"catalog", "registry"}:
            raw = raw.replace(b"\r\n", b"\n")
        hashes[name] = sha256(raw)
        if hashes[name] != contract.get("snapshot_sha256", {}).get(name):
            raise SnapshotRejected("SNAPSHOT_DIGEST_MISMATCH")
        documents[name] = json.loads(raw)
    if documents["graph"].get("metadata", {}).get("clinical_inference_performed") is not False:
        raise SnapshotRejected("GRAPH_SCOPE_MISMATCH")
    return {**documents, "contract": contract,
            "hashes": {**hashes, "contract": sha256(contract_bytes)}}


def _result(snapshot, reasons, citations=None, module_id=None):
    citations = citations or []
    return {
        "schema": "emergency-rag-provenance-result-v1",
        "task_id": TASK_ID,
        "status": "ABSTAIN" if reasons else "RETRIEVED_METADATA",
        "reasons": reasons,
        "module_id": module_id,
        "citations": citations,
        "source_commit": snapshot["contract"]["source_commit"],
        "snapshot_sha256": deepcopy(snapshot["hashes"]),
        "scope": "catalog_metadata_only_not_clinical_evidence_answer",
        "source_content_retrieved": False,
        "clinical_generation_performed": False,
        "can_answer_clinical_question": False,
        "runtime_activation_authorized": False,
        "clinical": "CLINICALLY_PENDING",
        "release": "NO_GO_CLINICAL_RELEASE",
    }


class RetrievalAbstained(ValueError):
    """An internal static abstention code, without private input."""


def _query_guard(query):
    allowed = {"synthetic", "module_id", "source_id", "expected_version"}
    if (not isinstance(query, dict) or set(query) - allowed
            or query.get("synthetic") is not True
            or not isinstance(query.get("module_id"), str)
            or IDENTIFIER.fullmatch(query["module_id"]) is None
            or len(query["module_id"]) > 100):
        raise RetrievalAbstained("SYNTHETIC_IDENTIFIER_QUERY_REQUIRED")
    source_id = query.get("source_id")
    if source_id is not None and (not isinstance(source_id, str)
            or IDENTIFIER.fullmatch(source_id) is None or len(source_id) > 100):
        raise RetrievalAbstained("SYNTHETIC_IDENTIFIER_QUERY_REQUIRED")
    expected_version = query.get("expected_version")
    if expected_version is not None and (not isinstance(expected_version, str)
            or not 1 <= len(expected_version) <= 512):
        raise RetrievalAbstained("INVALID_VERSION_CONSTRAINT")


def _module_and_refs(snapshot, module_id):
    catalog, graph, registry = (snapshot[name] for name in ("catalog", "graph", "registry"))
    module = registry.get("modules", {}).get(module_id)
    refs = catalog.get("module_sources", {}).get(module_id)
    if not isinstance(module, dict) or not isinstance(refs, list):
        raise RetrievalAbstained("MODULE_NOT_FOUND")
    module_nodes = [node for node in graph.get("nodes", []) if node.get("id") == "module:" + module_id]
    if len(module_nodes) != 1 or module_nodes[0].get("type") != "clinical_module":
        raise RetrievalAbstained("GRAPH_MODULE_MISMATCH")
    if module_nodes[0].get("evidence_status") != module.get("status"):
        raise RetrievalAbstained("GRAPH_MODULE_MISMATCH")
    return module, refs


def _canonical_ref(refs, source_id):
    if source_id is not None:
        selected = [ref for ref in refs if ref.get("source_id") == source_id]
        if not selected:
            raise RetrievalAbstained("SOURCE_NOT_LINKED_TO_MODULE")
        if any(ref.get("role") != "canonical_registry_identity" for ref in selected):
            raise RetrievalAbstained("HISTORICAL_COMPONENT_UNRECONCILED")
    else:
        selected = [ref for ref in refs if ref.get("role") == "canonical_registry_identity"]
    if len(selected) != 1:
        raise RetrievalAbstained("CANONICAL_SOURCE_AMBIGUOUS_OR_MISSING")
    return selected[0]


def _source_item(catalog, source_id):
    indexed = [(index, value) for index, value in enumerate(catalog.get("sources", []))
               if value.get("source_id") == source_id]
    if len(indexed) != 1:
        raise RetrievalAbstained("CANONICAL_SOURCE_AMBIGUOUS_OR_MISSING")
    return indexed[0]


def _source_guard(source, module, expected_version):
    if source.get("compound_identity") is not False:
        raise RetrievalAbstained("COMPOUND_SOURCE_IDENTITY_UNRESOLVED")
    if not isinstance(source.get("version"), str) or not source["version"].strip():
        raise RetrievalAbstained("SOURCE_VERSION_UNKNOWN")
    if expected_version is not None and expected_version != source["version"]:
        raise RetrievalAbstained("SOURCE_VERSION_MISMATCH")
    if (source.get("title"), source.get("version"), source.get("url")) != (
            module.get("primary_source"), module.get("stored_version"), module.get("primary_source_url")):
        raise RetrievalAbstained("CANONICAL_REGISTRY_RECONCILIATION_REQUIRED")
    if source.get("url") is not None and not str(source["url"]).startswith("https://"):
        raise RetrievalAbstained("CITATION_URL_NOT_PERMITTED")


def _graph_source_guard(graph, module_id, source, ref):
    source_id = source["source_id"]
    source_nodes = [node for node in graph.get("nodes", []) if node.get("id") == "source:" + source_id]
    edges = [edge for edge in graph.get("edges", [])
             if edge.get("source") == "module:" + module_id and edge.get("target") == "source:" + source_id
             and edge.get("type") == "SUPPORTED_BY"]
    if (len(source_nodes) != 1 or source_nodes[0].get("type") != "evidence_source"
            or len(edges) != 1 or any(edges[0].get(key) != ref.get(key) for key in ("role", "claim_scope"))
            or any(source_nodes[0].get("label" if field == "title" else field) != source.get(field)
                   for field in FIELDS if field != "source_id")):
        raise RetrievalAbstained("GRAPH_SOURCE_RELATION_MISMATCH")


def _metadata_citation(snapshot, module_id, module, refs, ref, index, source):
    return {
        "metadata": {field: deepcopy(source.get(field)) for field in FIELDS},
        "catalog_path": CATALOG_PATH,
        "catalog_json_pointer": "/sources/" + str(index),
        "module_relation_json_pointer": "/module_sources/" + module_id + "/" + str(refs.index(ref)),
        "catalog_url": "https://github.com/JuanCopado/Emergency/blob/" + snapshot["contract"]["source_commit"] + "/" + CATALOG_PATH,
        "source_record_sha256": sha256(_canonical_bytes(source)),
        "role": ref["role"],
        "claim_scope": ref.get("claim_scope"),
        "evidence_status_unchanged": module.get("status"),
        "rights_scope": "user_authorized_local_catalog_metadata_only_not_source_text_or_production_rights",
    }


def retrieve(snapshot, query):
    """Resolve exact synthetic IDs with abstention; no free-text/semantic fallback."""
    _validate_contract(snapshot["contract"])
    try:
        _query_guard(query)
        module_id = query["module_id"]
        module, refs = _module_and_refs(snapshot, module_id)
        ref = _canonical_ref(refs, query.get("source_id"))
        index, source = _source_item(snapshot["catalog"], ref["source_id"])
        _source_guard(source, module, query.get("expected_version"))
        _graph_source_guard(snapshot["graph"], module_id, source, ref)
        citation = _metadata_citation(snapshot, module_id, module, refs, ref, index, source)
    except RetrievalAbstained as error:
        return _result(snapshot, [str(error)])
    return _result(snapshot, [], [citation], module_id)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True, type=input_file, help="Existing graph inside the operator-granted input root")
    parser.add_argument("--query", required=True, type=input_file, help="Synthetic structured identifier query; no patient text")
    args = parser.parse_args(argv)
    try:
        snapshot = load_snapshot(args.graph)
        result = retrieve(snapshot, json.loads(args.query.read_text(encoding="utf-8")))
    except SnapshotRejected as error:
        result = {"status": "ABSTAIN", "reasons": [str(error)], "citations": [],
                  "runtime_activation_authorized": False, "clinical": "CLINICALLY_PENDING",
                  "release": "NO_GO_CLINICAL_RELEASE"}
    except (OSError, ValueError, KeyError, TypeError):
        result = {"status": "ABSTAIN", "reasons": ["INVALID_OR_UNAVAILABLE_SNAPSHOT_OR_QUERY"],
                  "citations": [], "runtime_activation_authorized": False,
                  "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE"}
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "ABSTAIN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
