"""Focused contracts for offline synthetic provenance retrieval, not graph generation."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "clinical/scripts"))
from rag_provenance_retrieval import (  # noqa: E402
    CATALOG_PATH, CONTRACT_PATH, FIELDS, REGISTRY_PATH, SnapshotRejected,
    load_snapshot, retrieve, sha256,
)


def fixture_snapshot():
    """A small in-memory test fixture; never materializes a second project graph."""
    catalog_raw = (ROOT / CATALOG_PATH).read_bytes()
    registry_raw = (ROOT / REGISTRY_PATH).read_bytes()
    contract_raw = (ROOT / CONTRACT_PATH).read_bytes()
    catalog, registry, contract = map(json.loads, (catalog_raw, registry_raw, contract_raw))
    nodes, edges = [], []
    for module_id in ("acute-coronary-syndrome", "cns-infection"):
        nodes.append({"id": "module:" + module_id, "type": "clinical_module",
                      "evidence_status": registry["modules"][module_id]["status"]})
        for ref in catalog["module_sources"][module_id]:
            source = next(item for item in catalog["sources"] if item["source_id"] == ref["source_id"])
            node = {"id": "source:" + source["source_id"], "type": "evidence_source"}
            node.update({"label" if field == "title" else field: source.get(field)
                         for field in FIELDS if field != "source_id"})
            nodes.append(node)
            edges.append({"source": "module:" + module_id, "target": "source:" + source["source_id"],
                          "type": "SUPPORTED_BY", "role": ref["role"], "claim_scope": ref["claim_scope"]})
    return {"catalog": catalog, "registry": registry, "contract": contract,
            "graph": {"metadata": {"clinical_inference_performed": False}, "nodes": nodes, "edges": edges},
            "hashes": {"catalog": sha256(catalog_raw), "registry": sha256(registry_raw),
                       "graph": "synthetic_in_memory_test_fixture", "contract": sha256(contract_raw)}}


class ProvenanceRetrieval(unittest.TestCase):
    def setUp(self):
        self.snapshot = fixture_snapshot()
        self.query = {"synthetic": True, "module_id": "acute-coronary-syndrome"}

    def assert_abstains(self, reason, query=None):
        result = retrieve(self.snapshot, self.query if query is None else query)
        self.assertEqual(result["status"], "ABSTAIN")
        self.assertEqual(result["reasons"], [reason])
        self.assertEqual(result["citations"], [])
        self.assertFalse(result["runtime_activation_authorized"])
        return result

    def test_exact_citation_round_trips_to_current_record_and_version(self):
        result = retrieve(self.snapshot, self.query)
        self.assertEqual(result["status"], "RETRIEVED_METADATA")
        citation = result["citations"][0]
        index = int(citation["catalog_json_pointer"].split("/")[-1])
        source = self.snapshot["catalog"]["sources"][index]
        self.assertEqual(citation["metadata"], {field: source.get(field) for field in FIELDS})
        self.assertEqual(citation["metadata"]["version"], self.snapshot["registry"]["modules"]["acute-coronary-syndrome"]["stored_version"])
        self.assertIn(result["source_commit"], citation["catalog_url"])
        self.assertFalse(result["can_answer_clinical_question"])
        self.assertFalse(result["source_content_retrieved"])
        self.assertEqual(citation["metadata"]["license_status"], "unknown")
        self.assertFalse(self.snapshot["contract"]["production_rights_granted"])

    def test_unknown_identifiers_do_not_echo_free_text_or_path_content(self):
        for query in ({"synthetic": True, "module_id": "unknown-synthetic-module"},
                      {"synthetic": True, "module_id": "../../private-patient"},
                      {**self.query, "patient_note": "PRIVATE_SENTINEL"}, {**self.query, "synthetic": False}):
            result = retrieve(self.snapshot, query)
            self.assertEqual(result["status"], "ABSTAIN")
            self.assertNotIn("PRIVATE_SENTINEL", json.dumps(result))
            self.assertNotIn("../../", json.dumps(result))
            self.assertIsNone(result["module_id"])

    def test_source_not_linked_to_module_never_falls_back(self):
        self.assert_abstains("SOURCE_NOT_LINKED_TO_MODULE", {**self.query, "source_id": "src-who-meningitis-2025"})

    def test_historical_verified_license_does_not_become_current_source(self):
        self.assert_abstains("HISTORICAL_COMPONENT_UNRECONCILED", {
            "synthetic": True, "module_id": "cns-infection", "source_id": "src-who-meningitis-2025"})

    def test_compound_identity_does_not_fall_back_to_historical_components(self):
        self.assert_abstains("COMPOUND_SOURCE_IDENTITY_UNRESOLVED", {"synthetic": True, "module_id": "cns-infection"})

    def test_wrong_version_abstains_instead_of_selecting_near_match(self):
        self.assert_abstains("SOURCE_VERSION_MISMATCH", {**self.query, "expected_version": "SYNTHETIC-NONEXISTENT-VERSION"})

    def test_unknown_version_is_not_inferred_from_title_or_date(self):
        source = next(item for item in self.snapshot["catalog"]["sources"] if item["source_id"] == "src-b3266402")
        source["version"] = None
        self.assert_abstains("SOURCE_VERSION_UNKNOWN")

    def test_graph_source_edge_and_module_drift_fail_closed(self):
        for change in (lambda s: s["graph"]["nodes"][0].update(evidence_status="promoted"),
                       lambda s: s["graph"]["nodes"][1].update(version="invented"),
                       lambda s: s["graph"]["edges"].pop(0)):
            self.snapshot = fixture_snapshot()
            change(self.snapshot)
            self.assertEqual(retrieve(self.snapshot, self.query)["status"], "ABSTAIN")

    def test_catalog_to_registry_drift_requires_reconciliation(self):
        self.snapshot["registry"]["modules"]["acute-coronary-syndrome"]["stored_version"] = "changed"
        self.assert_abstains("CANONICAL_REGISTRY_RECONCILIATION_REQUIRED")

    def test_consumer_scope_cannot_authorize_text_generation_or_false_commit(self):
        for change in ({"licensed_source_content_fields": ["abstractText"]},
                       {"clinical_generation_enabled": True}, {"external_consumers_enabled": True},
                       {"source_commit": "0" * 40}):
            self.snapshot = fixture_snapshot()
            self.snapshot["contract"].update(change)
            with self.assertRaises(SnapshotRejected):
                retrieve(self.snapshot, self.query)

    def test_loading_modified_bytes_rejects_digest_before_retrieval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in (CATALOG_PATH, REGISTRY_PATH, CONTRACT_PATH):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes())
            graph = root / "existing-graph.json"
            graph.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(SnapshotRejected, "SNAPSHOT_DIGEST_MISMATCH"):
                load_snapshot(graph, root=root)

    def test_windows_crlf_checkout_keeps_canonical_git_metadata_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            graph_raw = b'{"metadata":{"clinical_inference_performed":false}}'
            contract = deepcopy(self.snapshot["contract"])
            contract["snapshot_sha256"]["graph"] = sha256(graph_raw)
            for path in (CATALOG_PATH, REGISTRY_PATH):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / path).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            contract_path = root / CONTRACT_PATH
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            graph = root / "synthetic-fixture.json"
            graph.write_bytes(graph_raw)
            snapshot = load_snapshot(graph, root=root)
            self.assertEqual(snapshot["catalog"], self.snapshot["catalog"])
            self.assertEqual(snapshot["hashes"]["catalog"], contract["snapshot_sha256"]["catalog"])

    def test_retrieval_never_mutates_catalog_evidence_or_contract(self):
        before = deepcopy(self.snapshot)
        result = retrieve(self.snapshot, self.query)
        result["citations"][0]["metadata"]["title"] = "OUTPUT_ONLY"
        self.assertEqual(self.snapshot, before)


if __name__ == "__main__":
    unittest.main()
