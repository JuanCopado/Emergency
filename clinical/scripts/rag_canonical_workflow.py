"""One explicitly authorized project workflow; exact binding and bounded spans only."""
from pathlib import Path

from rag_provenance_retrieval import SOURCE_COMMIT, sha256

SOURCE_ID = "src-internal-image-safety-workflow"
MODULE_ID = "clinical-image-interpretation"
SOURCE_PATH = "clinical/modules/clinical-images.md"
SOURCE_SHA256 = "ec1e12141ee3cdc864f1c2e1071a1877dd859634ac1157bf882448db1167780a"
COPY_VERSION = "git:" + SOURCE_COMMIT
INDEX_PATH = "clinical/references/module-index.md"
INDEX_SHA256 = "1e06e639bb7e89487b4ac6dfbdc4ea534ef1f2cf59f161eb75f937657ac52301"
INDEX_LINE = 96
INDEX_LITERAL = "| clinical-image-interpretation | `modules/clinical-images.md` |"
BINDING_ROLE = "historical_component_pending_reconciliation"
CLAIM_SCOPE = "image intake, quality, uncertainty and abstention"
SPANS = [
    {"start_line": 3, "end_line": 15, "utf8_lf_sha256": "8f120b409fe1080fc2ce948d7aefa5975e1f41d5a7c5518fe5babc233043d07b"},
    {"start_line": 35, "end_line": 47, "utf8_lf_sha256": "9742540724432e20633298cccafd45cd2586ad53a7e59b2bd4f2f7388d73a068"},
]
CITATION_FIELDS = ("declared_canonical_version", "binding_role", "binding_module_id", "binding_claim_scope",
                   "binding_source_json_pointer", "binding_relation_json_pointer", "module_index_path",
                   "module_index_line", "module_index_sha256", "evidence_status_unchanged",
                   "authorized_span_start", "authorized_span_end", "authorized_span_sha256")


class WorkflowRejected(ValueError):
    """Static refusal, never document text."""


def validate_identity(item):
    actual = (item.get("source_id"), item.get("source_class"), item.get("path"), item.get("sha256"), item.get("version"))
    if actual != (SOURCE_ID, "project_owned_workflow", SOURCE_PATH, SOURCE_SHA256, COPY_VERSION):
        raise WorkflowRejected("CANONICAL_WORKFLOW_IDENTITY_MISMATCH")
    if item.get("allowed_spans") != SPANS or item.get("permission", {}).get("authorized_spans") != SPANS:
        raise WorkflowRejected("CANONICAL_WORKFLOW_SPANS_NOT_AUTHORIZED")


def _catalog_binding(snapshot):
    records = [(index, source) for index, source in enumerate(snapshot["catalog"]["sources"]) if source.get("source_id") == SOURCE_ID]
    if len(records) != 1:
        raise WorkflowRejected("CANONICAL_WORKFLOW_BINDING_MISMATCH")
    index, source = records[0]
    identity = (source.get("provenance"), source.get("source_type"), source.get("organization"), source.get("license_status"), source.get("version"))
    if identity != ("repository_internal_workflow", "internal_workflow", "Emergency project", "verified", None):
        raise WorkflowRejected("CANONICAL_WORKFLOW_BINDING_MISMATCH")
    refs = snapshot["catalog"]["module_sources"].get(MODULE_ID, [])
    found = [(number, ref) for number, ref in enumerate(refs) if ref.get("source_id") == SOURCE_ID]
    if len(found) != 1 or (found[0][1].get("role"), found[0][1].get("claim_scope")) != (BINDING_ROLE, CLAIM_SCOPE):
        raise WorkflowRejected("CANONICAL_WORKFLOW_BINDING_MISMATCH")
    return index, source, found[0][0]


def _graph_binding(snapshot):
    graph = snapshot["graph"]
    nodes = {node["id"]: node for node in graph["nodes"]}
    module = nodes.get("module:" + MODULE_ID, {})
    source = nodes.get("source:" + SOURCE_ID, {})
    if (module.get("type"), module.get("evidence_status"), source.get("type"), source.get("version")) != (
            "clinical_module", "yellow", "evidence_source", None):
        raise WorkflowRejected("CANONICAL_WORKFLOW_BINDING_MISMATCH")
    supported = {"source": "module:" + MODULE_ID, "target": "source:" + SOURCE_ID,
                 "type": "SUPPORTED_BY", "role": BINDING_ROLE, "claim_scope": CLAIM_SCOPE}
    located = {"source": "module:" + MODULE_ID, "target": "bundle:modules/clinical-images.md", "type": "LOCATED_IN"}
    if supported not in graph.get("edges", []) or located not in graph.get("edges", []):
        raise WorkflowRejected("CANONICAL_WORKFLOW_BINDING_MISMATCH")
    return module["evidence_status"]


def _module_index_binding(root):
    path = (root / INDEX_PATH).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise WorkflowRejected("CANONICAL_MODULE_INDEX_MISMATCH")
    raw = path.read_bytes().replace(b"\r\n", b"\n")
    if sha256(raw) != INDEX_SHA256 or raw.decode("utf-8").splitlines()[INDEX_LINE - 1] != INDEX_LITERAL:
        raise WorkflowRejected("CANONICAL_MODULE_INDEX_MISMATCH")


def validate_binding(snapshot, root):
    index, source, relation_index = _catalog_binding(snapshot)
    status = _graph_binding(snapshot)
    _module_index_binding(root)
    return {"declared_canonical_version": source["version"], "binding_role": BINDING_ROLE,
            "binding_module_id": MODULE_ID, "binding_claim_scope": CLAIM_SCOPE,
            "binding_source_json_pointer": "/sources/" + str(index),
            "binding_relation_json_pointer": "/module_sources/" + MODULE_ID + "/" + str(relation_index),
            "module_index_path": INDEX_PATH, "module_index_line": INDEX_LINE,
            "module_index_sha256": INDEX_SHA256, "evidence_status_unchanged": status}


def sections(text, binding):
    """Keep original one-based line coordinates; no outside text is indexed."""
    lines = text.splitlines(keepends=True)
    result = []
    for span in SPANS:
        selected = "".join(lines[span["start_line"] - 1:span["end_line"]])
        if sha256(selected.encode("utf-8")) != span["utf8_lf_sha256"]:
            raise WorkflowRejected("CANONICAL_WORKFLOW_SPAN_HASH_MISMATCH")
        metadata = {**binding, "authorized_span_start": span["start_line"], "authorized_span_end": span["end_line"],
                    "authorized_span_sha256": span["utf8_lf_sha256"]}
        result.append((selected, span["start_line"] - 1, metadata))
    return result
