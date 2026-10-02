#!/usr/bin/env python3
"""Build a deterministic project knowledge graph from normalized evidence metadata.

The graph captures provenance and project structure only. It performs no clinical
inference and does not create treatment recommendations.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve()
CLINICAL_ROOT = HERE.parents[1]
REPO_ROOT = CLINICAL_ROOT.parent
ROW = re.compile(r"^\| ([a-z0-9-]+) \| `([^`]+)` \|$")


def build_graph(clinical_root: Path = CLINICAL_ROOT) -> dict:
    manifest_path = clinical_root / "references" / "module-index.md"
    registry_path = clinical_root / "references" / "evidence-registry.json"
    sources_path = clinical_root / "references" / "evidence-sources.json"

    rows: list[tuple[str, str]] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2)))

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    evidence = registry.get("modules", {})
    source_doc = json.loads(sources_path.read_text(encoding="utf-8"))
    sources = {item["source_id"]: item for item in source_doc.get("sources", [])}
    module_sources = source_doc.get("module_sources", {})

    manifest_ids = {module_id for module_id, _ in rows}
    evidence_ids = set(evidence)
    source_map_ids = set(module_sources)

    if manifest_ids != evidence_ids:
        raise ValueError(
            "Manifest/evidence mismatch: "
            f"missing_evidence={sorted(manifest_ids - evidence_ids)}; "
            f"missing_manifest={sorted(evidence_ids - manifest_ids)}"
        )
    if manifest_ids != source_map_ids:
        raise ValueError(
            "Manifest/source-map mismatch: "
            f"missing_source_map={sorted(manifest_ids - source_map_ids)}; "
            f"unknown_source_map={sorted(source_map_ids - manifest_ids)}"
        )

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    for module_id, bundle_path in rows:
        rec = evidence[module_id]
        status = (rec.get("status") or "unknown").strip()
        module_node = {
            "id": f"module:{module_id}",
            "type": "clinical_module",
            "label": module_id,
            "evidence_status": status,
            "priority": rec.get("priority"),
            "last_checked": rec.get("last_checked"),
        }
        nodes[module_node["id"]] = module_node

        bundle_id = f"bundle:{bundle_path}"
        nodes.setdefault(
            bundle_id,
            {"id": bundle_id, "type": "module_bundle", "label": bundle_path},
        )
        edges.append(
            {"source": module_node["id"], "target": bundle_id, "type": "LOCATED_IN"}
        )

        refs = module_sources.get(module_id, [])
        if not refs:
            raise ValueError(f"{module_id}: no normalized evidence source")
        for ref in refs:
            source_id = ref.get("source_id")
            source = sources.get(source_id)
            if not source:
                raise ValueError(f"{module_id}: unknown source_id {source_id}")

            graph_source_id = f"source:{source_id}"
            nodes.setdefault(
                graph_source_id,
                {
                    "id": graph_source_id,
                    "type": "evidence_source",
                    "label": source.get("title"),
                    "organization": source.get("organization"),
                    "source_type": source.get("source_type"),
                    "url": source.get("url"),
                    "persistent_id": source.get("persistent_id"),
                    "version": source.get("version"),
                    "publication_date": source.get("publication_date"),
                    "last_verified": source.get("last_verified"),
                    "language": source.get("language"),
                    "jurisdiction": source.get("jurisdiction"),
                    "license_status": source.get("license_status"),
                    "compound_identity": source.get("compound_identity", False),
                },
            )
            edges.append(
                {
                    "source": module_node["id"],
                    "target": graph_source_id,
                    "type": "SUPPORTED_BY",
                    "role": ref.get("role"),
                    "claim_scope": ref.get("claim_scope"),
                }
            )

    status_counts: dict[str, int] = {}
    for node in nodes.values():
        if node.get("type") == "clinical_module":
            status = node.get("evidence_status") or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

    source_nodes = [n for n in nodes.values() if n.get("type") == "evidence_source"]
    compound_sources = sum(1 for n in source_nodes if n.get("compound_identity"))

    return {
        "schema_version": "1.1",
        "generated_from": [
            "clinical/references/module-index.md",
            "clinical/references/evidence-registry.json",
            "clinical/references/evidence-sources.json",
        ],
        "metadata": {
            "module_count": len(rows),
            "source_count": len(source_nodes),
            "compound_source_count": compound_sources,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "evidence_status_counts": status_counts,
            "clinical_inference_performed": False,
        },
        "nodes": sorted(nodes.values(), key=lambda x: x["id"]),
        "edges": sorted(
            edges, key=lambda x: (x["source"], x["type"], x["target"])
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=str(
            REPO_ROOT / "knowledge-graph" / "generated" / "project-graph.json"
        ),
    )
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    graph = build_graph()
    output.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(graph["metadata"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
