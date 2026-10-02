import importlib.util
import json
import unittest
from pathlib import Path

CLINICAL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = CLINICAL_ROOT / "scripts" / "build_project_graph.py"
SPEC = importlib.util.spec_from_file_location("build_project_graph", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ProjectGraphTests(unittest.TestCase):
    def test_graph_covers_manifest_and_evidence_registry(self):
        graph = MOD.build_graph()
        meta = graph["metadata"]
        modules = [n for n in graph["nodes"] if n["type"] == "clinical_module"]
        sources = [n for n in graph["nodes"] if n["type"] == "evidence_source"]
        self.assertEqual(meta["module_count"], len(modules))
        self.assertEqual(meta["source_count"], len(sources))
        self.assertGreaterEqual(meta["module_count"], 100)
        self.assertGreaterEqual(meta["source_count"], 1)
        self.assertFalse(meta["clinical_inference_performed"])

    def test_all_modules_have_source_and_bundle_edges(self):
        graph = MOD.build_graph()
        outgoing = {}
        for edge in graph["edges"]:
            outgoing.setdefault(edge["source"], set()).add(edge["type"])
        for node in graph["nodes"]:
            if node["type"] == "clinical_module":
                self.assertIn("LOCATED_IN", outgoing[node["id"]])
                self.assertIn("SUPPORTED_BY", outgoing[node["id"]])

    def test_normalized_sources_have_required_traceability_fields(self):
        graph = MOD.build_graph()
        required = {
            "organization", "source_type", "url", "persistent_id", "version",
            "publication_date", "last_verified", "language", "jurisdiction",
            "license_status", "compound_identity",
        }
        for node in graph["nodes"]:
            if node["type"] == "evidence_source":
                self.assertTrue(required.issubset(node.keys()))

    def test_source_catalog_maps_every_module(self):
        source_doc = json.loads(
            (CLINICAL_ROOT / "references/evidence-sources.json").read_text(
                encoding="utf-8"
            )
        )
        module_sources = source_doc["module_sources"]
        self.assertEqual(len(module_sources), 106)
        self.assertTrue(all(module_sources.values()))


if __name__ == "__main__":
    unittest.main()
