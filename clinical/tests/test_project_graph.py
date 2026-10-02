import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_project_graph.py"
SPEC = importlib.util.spec_from_file_location("build_project_graph", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ProjectGraphTests(unittest.TestCase):
    def test_graph_covers_manifest_and_evidence_registry(self):
        graph = MOD.build_graph()
        meta = graph["metadata"]
        modules = [n for n in graph["nodes"] if n["type"] == "clinical_module"]
        self.assertEqual(meta["module_count"], len(modules))
        self.assertGreaterEqual(meta["module_count"], 100)
        self.assertFalse(meta["clinical_inference_performed"])
        self.assertEqual(meta["edge_count"], meta["module_count"] * 2)

    def test_all_modules_have_source_and_bundle_edges(self):
        graph = MOD.build_graph()
        outgoing = {}
        for edge in graph["edges"]:
            outgoing.setdefault(edge["source"], set()).add(edge["type"])
        for node in graph["nodes"]:
            if node["type"] == "clinical_module":
                self.assertEqual(
                    outgoing[node["id"]], {"LOCATED_IN", "SUPPORTED_BY"}
                )


if __name__ == "__main__":
    unittest.main()
