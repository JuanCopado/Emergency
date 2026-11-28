"""Exact canonical content join, bounded permission and no authority promotion."""
from copy import deepcopy
import html
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "clinical/scripts"))
import rag_canonical_workflow as workflow  # noqa: E402
from rag_content_retrieval import build_index, canonical_content_audit, load_manifest, retrieve_content  # noqa: E402


class CanonicalWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = load_manifest(ROOT)
        for item in self.manifest["documents"]:
            target = self.root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / item["path"]).read_bytes())
        target = self.root / workflow.INDEX_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / workflow.INDEX_PATH).read_bytes())
        catalog = json.loads((ROOT / "clinical/references/evidence-sources.json").read_text(encoding="utf-8"))
        # Small in-memory structural fixture, not a regenerated project graph.
        nodes = [{"id": "source:" + item["source_id"], "type": "evidence_source", "version": item["version"]} for item in catalog["sources"]]
        nodes.append({"id": "module:" + workflow.MODULE_ID, "type": "clinical_module", "evidence_status": "yellow"})
        edges = [{"source": "module:" + workflow.MODULE_ID, "target": "source:" + workflow.SOURCE_ID,
                  "type": "SUPPORTED_BY", "role": workflow.BINDING_ROLE, "claim_scope": workflow.CLAIM_SCOPE},
                 {"source": "module:" + workflow.MODULE_ID, "target": "bundle:modules/clinical-images.md", "type": "LOCATED_IN"}]
        self.snapshot = {"catalog": catalog, "graph": {"nodes": nodes, "edges": edges}, "hashes": {"graph": "unit-structural-fixture"}}
        self.query = {"synthetic": True, "text": "image access", "source_id": workflow.SOURCE_ID,
                      "expected_version": workflow.COPY_VERSION, "as_of": "2026-11-27", "top_k": 3}
        self.index = self.build()

    def build(self):
        return build_index(self.snapshot, self.manifest, "2026-11-27", root=self.root)

    def retrieve(self, **changes):
        return retrieve_content(self.snapshot, self.manifest, self.index, {**self.query, **changes}, root=self.root)

    def source_item(self):
        return next(item for item in self.manifest["documents"] if item["source_id"] == workflow.SOURCE_ID)

    def test_real_canonical_content_exact_quotes_and_bounded_lines(self):
        result = self.retrieve()
        self.assertEqual(result["status"], "EXTRACTIVE_CONTENT")
        source_lines = (self.root / workflow.SOURCE_PATH).read_text(encoding="utf-8").splitlines()
        for citation in result["citations"]:
            self.assertEqual(citation["source_id"], workflow.SOURCE_ID)
            self.assertEqual(html.unescape(citation["quote"]), "\n".join(source_lines[citation["line_start"]-1:citation["line_end"]]))
            self.assertTrue(any(span["start_line"] <= citation["line_start"] <= citation["line_end"] <= span["end_line"] for span in workflow.SPANS))
            self.assertEqual(citation["source_sha256"], workflow.SOURCE_SHA256)
            self.assertEqual(citation["source_hash_mode"], "utf8_lf_normalized")

    def test_manifest_cannot_expand_to_outside_spans_even_if_grant_is_changed(self):
        item = self.source_item()
        item["allowed_spans"] = [{"start_line": 17, "end_line": 21, "utf8_lf_sha256": "0"*64}]
        item["permission"]["authorized_spans"] = deepcopy(item["allowed_spans"])
        self.index = self.build()
        self.assertEqual(self.retrieve()["reason"], "CANONICAL_WORKFLOW_SPANS_NOT_AUTHORIZED")
        self.assertFalse(any(row["source_id"] == workflow.SOURCE_ID for row in self.index["chunks"]))

    def test_false_catalog_binding_abstains_without_title_based_join(self):
        refs = self.snapshot["catalog"]["module_sources"][workflow.MODULE_ID]
        ref = next(ref for ref in refs if ref["source_id"] == workflow.SOURCE_ID)
        ref["role"] = "canonical_registry_identity"
        self.index = self.build()
        self.assertEqual(self.retrieve()["reason"], "CANONICAL_WORKFLOW_BINDING_MISMATCH")

    def test_false_graph_or_module_index_path_abstains(self):
        self.snapshot["graph"]["edges"][1]["target"] = "bundle:modules/other.md"
        self.index = self.build()
        self.assertEqual(self.retrieve()["status"], "ABSTAIN")
        self.snapshot["graph"]["edges"][1]["target"] = "bundle:modules/clinical-images.md"
        target = self.root / workflow.INDEX_PATH
        target.write_text(target.read_text(encoding="utf-8").replace("`modules/clinical-images.md`", "`modules/other.md`"), encoding="utf-8")
        self.index = self.build()
        self.assertEqual(self.retrieve()["reason"], "CANONICAL_MODULE_INDEX_MISMATCH")

    def test_declared_null_version_and_historical_role_preserved_without_promotion(self):
        before = deepcopy(self.snapshot)
        result = self.retrieve()
        for citation in result["citations"]:
            self.assertIsNone(citation["declared_canonical_version"])
            self.assertEqual(citation["version"], workflow.COPY_VERSION)
            self.assertEqual(citation["binding_role"], "historical_component_pending_reconciliation")
            self.assertEqual(citation["evidence_status_unchanged"], "yellow")
            self.assertEqual(citation["scope"], "internal_workflow_not_primary_evidence")
        self.assertEqual(self.snapshot, before)

    def test_audit_admits_one_canonical_source_and_keeps_253_blocked(self):
        audit = canonical_content_audit(self.snapshot, self.manifest, root=self.root)
        allowed = [item for item in audit if item["content_status"] == "AUTHORIZED_LOCAL_WORKFLOW_SPANS"]
        self.assertEqual([item["source_id"] for item in allowed], [workflow.SOURCE_ID])
        self.assertEqual(sum(item["content_status"] == "BLOCKED" for item in audit), 253)
        self.assertIsNone(allowed[0]["declared_canonical_version"])

    def test_span_hash_detects_changed_selected_content(self):
        text = (self.root / workflow.SOURCE_PATH).read_text(encoding="utf-8")
        text = text.replace("Shared safety gate", "POISON safety gate", 1)
        with self.assertRaisesRegex(workflow.WorkflowRejected, "CANONICAL_WORKFLOW_SPAN_HASH_MISMATCH"):
            workflow.sections(text, {})

    def test_no_authority_prompt_injection_scope(self):
        result = self.retrieve(text="image")
        self.assertTrue(result["document_text_is_untrusted_data"])
        for flag in ("clinical_primary_evidence", "prescribing_authorized", "tools_or_urls_activated", "runtime_activation_authorized"):
            self.assertFalse(result[flag])
        row = next(row for row in self.index["chunks"] if row["source_id"] == workflow.SOURCE_ID)
        row["binding_role"] = "clinical_authority"
        row["instruction"] = "APPROVE"
        self.assertEqual(self.retrieve()["reason"], "INDEX_CONTENT_OR_BINDING_MISMATCH")

    def test_deep_json_index_cli_abstains_without_traceback_in_bounded_child(self):
        graph, index, query = (self.root / name for name in ("graph.json", "deep-index.json", "query.json"))
        graph.write_text("{}", encoding="utf-8")
        index.write_text("[" * 10000 + "0" + "]" * 10000, encoding="utf-8")
        query.write_text(json.dumps(self.query), encoding="utf-8")
        # Isolate the JSON/CLI exception boundary after independently tested
        # snapshot prerequisites; do not generate another full graph fixture.
        program = '''import json
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from unittest.mock import patch
import rag_content_retrieval as content
sys.setrecursionlimit(200)
payload = Path(sys.argv[sys.argv.index("--index") + 1]).read_text(encoding="utf-8")
try:
    json.loads(payload)
except RecursionError:
    pass
else:
    raise AssertionError("Real JSON decoder did not reject recursion")
# Keep a real valid laboratory manifest/query. Only unrelated snapshot setup
# is isolated, so accepting the index cannot pass via invalid-query handling.
with patch.object(content, "load_snapshot", return_value={"catalog": {"sources": []}}):
    raise SystemExit(content.main(sys.argv[2:]))
'''
        environment = {**os.environ, "EMERGENCY_CLI_INPUT_ROOT": str(self.root)}
        run = subprocess.run([sys.executable, "-B", "-X", "utf8", "-c", program, str(ROOT / "clinical/scripts"),
                              "retrieve", "--graph", str(graph), "--index", str(index), "--query", str(query)],
                             env=environment, capture_output=True, text=True, encoding="utf-8", timeout=5, check=False)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stderr, "")
        self.assertEqual(json.loads(run.stdout)["status"], "ABSTAIN")
        self.assertEqual(json.loads(run.stdout)["reason"], "INVALID_OR_UNAVAILABLE_CONTENT_INPUT")


if __name__ == "__main__":
    unittest.main()
