"""Verify the real stdio MCP contract using only project metadata and synthetic negatives."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
from client_probe import probe

ROOT = Path(__file__).resolve().parents[2]
MODULE = "adrenal-crisis"
MEDICATION = "SUB-4-factor-prothrombin-complex-concentrate"
DECISION = "MED-DEC-R46-01"
CALLS = [
    {"name": "get_project_state"},
    {"name": "get_clinical_module", "arguments": {"module_id": MODULE}},
    {"name": "search_evidence", "arguments": {"query": "NICE", "limit": 1}},
    {"name": "get_medication_reference", "arguments": {"medication_id": MEDICATION}},
    {"name": "get_owner_decision", "arguments": {"decision_id": DECISION}},
    {"name": "get_pending_tasks", "arguments": {"limit": 2}},
    {"name": "get_qa_status"},
    {"name": "get_graph_neighbors", "arguments": {"node_id": "module:"+MODULE, "limit": 2}},
    {"name": "get_clinical_module", "arguments": {"module_id": "../.env"}},
    {"name": "get_clinical_module", "arguments": {"module_id": MODULE, "include_content": True}},
    {"name": "get_project_state", "arguments": {"root": "../.env"}},
]
TOOL_NAMES = {row["name"] for row in CALLS}

def check(condition):
    if not condition:
        raise ValueError("MCP_PROTOCOL_CONTRACT_FAILED")

def verify(receipt):
    check(receipt["initialize"] == "PASS")
    check({row["name"] for row in receipt["tools"]} == TOOL_NAMES)
    check(len(receipt["tools"]) == 8 and len(receipt["calls"]) == 11)
    for tool in receipt["tools"]:
        annotations = tool["annotations"]
        check(annotations["read_only_hint"] is True and annotations["destructive_hint"] is False)
        check(annotations["open_world_hint"] is False)
    values = []
    for row in receipt["calls"][:8]:
        response = row["response"]
        check(row["is_error"] is False and response["is_error"] is False)
        value = response["structured_content"]
        check(value["permission_scope"] == "metadata")
        check(value["clinical"] == "CLINICALLY_PENDING" and value["release"] == "NO_GO_CLINICAL_RELEASE")
        check(value["write_performed"] is False and value["network_used"] is False)
        check(value["prescribing_authorized"] is False and bool(value["provenance"]))
        values.append(value["result"])
    check(values[0]["module_count"] == 131 and values[0]["knowledge_graph"]["node_count"] == 397)
    check(values[0]["knowledge_graph"]["edge_count"] == 417)
    check(values[1]["module_id"] == MODULE and values[1]["content_returned"] is False)
    check("content" not in values[1])
    check(values[2]["matches"] and values[2]["fulltext_read_or_permission_inferred"] is False)
    check(values[3]["reference"]["id"] == MEDICATION and values[3]["not_an_administration_instruction"] is True)
    check(values[4]["decision_id"] == DECISION and values[4]["records"])
    check(values[4]["new_approval_claimed"] is False)
    check(values[5]["version"] == 6 and len(values[5]["tasks"]) == 2)
    check(values[5]["freshness"] == "REPOSITORY_HISTORICAL_SNAPSHOT")
    check(values[6]["record"]["status"] == "PASS")
    check(values[6]["live_CI_or_audit_queried"] is False)
    check(values[7]["node"]["id"] == "module:"+MODULE and 0 < len(values[7]["edges"]) <= 2)
    for row in receipt["calls"][8:]:
        response = row["response"]
        check(row["is_error"] is True and response["is_error"] is True)
        check(response["structured_content"]["status"] == "ABSTAIN")
        check(response["structured_content"]["reason"] == "REQUEST_REJECTED_OR_SNAPSHOT_UNAVAILABLE")
        check("../.env" not in json.dumps(response))
    return {"initialize": "PASS", "tools_list": 8, "positive_calls_verified": 8,
            "negative_calls_verified": 3, "semantic_assertions": "PASS",
            "permission_scope": "metadata", "real_patient_data": False,
            "source_or_clinical_writes": False, "clinical_network_used": False,
            "tools": receipt["tools"],
            "calls": [{key: row[key] for key in ("tool", "is_error", "response_bytes", "response_sha256")}
                      for row in receipt["calls"]],
            "server_info": receipt["server_info"], "elapsed_ms": receipt["elapsed_ms"],
            "canonical_source_commit": "3cc5139b149feef390e6ceaa7358e2425d92620a",
            "clinical": "CLINICALLY_PENDING", "release": "NO_GO_CLINICAL_RELEASE",
            "receipt_scope": "Protocol and metadata only; not clinical validation or live CI certification."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec = {"command": sys.executable, "args": ["-B", "-X", "utf8",
            str(ROOT/"clinical/scripts/emergency_mcp_readonly.py")],
            "cwd": str(ROOT), "include_responses": True, "calls": CALLS}
    try:
        receipt = asyncio.run(probe(spec))
        summary = verify(receipt)
    except Exception:
        parser.exit(2, "MCP protocol verification failed; no caller, environment or source content logged\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf8", newline="\n")
    print(json.dumps({key: summary[key] for key in ("initialize", "tools_list", "positive_calls_verified",
                                                   "negative_calls_verified", "semantic_assertions")}))

if __name__ == "__main__":
    main()
