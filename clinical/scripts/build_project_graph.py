#!/usr/bin/env python3
"""Build a deterministic project knowledge graph from the clinical manifest.

The graph captures metadata and evidence provenance only. It does not infer
clinical relationships or create treatment recommendations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve()
CLINICAL_ROOT = HERE.parents[1]
REPO_ROOT = CLINICAL_ROOT.parent
ROW = re.compile(r"^\| ([a-z0-9-]+) \| `([^`]+)` \|$")


def source_id(url: str | None, name: str) -> str:
    raw = (url or name).strip()
    return "source:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_graph(clinical_root: Path = CLINICAL_ROOT) -> dict:
    manifest_path = clinical_root / "references" / "module-index.md"
    registry_path = clinical_root / "references" / "evidence-registry.json"

    rows: list[tuple[str, str]] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line.strip())
        if match:
            rows.append((match.group(1), match.group(2)))

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    evidence = registry.get("modules", {})
    manifest_ids = {module_id for module_id, _ in rows}
    evidence_ids = set(evidence)

    if manifest_ids != evidence_ids:
        raise ValueError(
            "Manifest/evidence mismatch: "
            f"missing_evidence={sorted(manifest_ids - evidence_ids)}; "
            f"missing_manifest={sorted(evidence_ids - manifest_ids)}"
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

        src_name = rec.get("primary_source") or "Unspecified primary source"
        src_url = rec.get("primary_source_url")
        sid = source_id(src_url, src_name)
        nodes.setdefault(
            sid,
            {
                "id": sid,
                "type": "evidence_source",
                "label": src_name,
                "url": src_url,
            },
        )
        edges.append(
            {"source": module_node["id"], "target": sid, "type": "SUPPORTED_BY"}
        )

    status_counts: dict[str, int] = {}
    for node in nodes.values():
        if node.get("type") == "clinical_module":
            status = node.get("evidence_status") or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "schema_version": "1.0",
        "generated_from": [
            "clinical/references/module-index.md",
            "clinical/references/evidence-registry.json",
        ],
        "metadata": {
            "module_count": len(rows),
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
