"""Claim-complete RAG selection and a nonclinical response-validation laboratory.

Existing phase2/3 source, version, permission, graph and contradiction gates remain
authoritative. No external provider, clinical generation or network transport.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
import time

import rag_phase3 as phase3
clinical = phase3.clinical
STOP_WORDS = frozenset(("a an and are as at be been by can could described do does for from "
    "how in is it of on or scenario should synthetic the this to what when which with would "
    "documented immediate assessment evaluate evaluation clinical patient adult normal question suspected urgent disease").split())
GENERIC_CONCEPTS = frozenset({"assessment", "normal"})
MAX_CITATIONS = 3
MAX_LAB_BYTES = 8192

class LabRejected(ValueError):
    """Static laboratory reason, never raw provider or document content."""

def require(condition, reason):
    if not condition:
        raise LabRejected(reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf8")

def citation_id(row):
    fields = ("document_id", "version", "path", "source_sha256", "line_start", "line_end")
    return sha(canonical({**{key: row[key] for key in fields}, "text_sha256": sha(row["text"].encode("utf8"))}))

def meaningful_rank(question, rows, mode="hybrid"):
    require(mode in phase3.MODES and isinstance(question, str), "INVALID_LAB_RANK_INPUT")
    require(isinstance(rows, list) and len(rows) <= 128, "LAB_CANDIDATE_LIMIT")
    tokens = {word: 1 for word in phase3.lexical_features(question) if word not in STOP_WORDS}
    concepts = {key: 1 for key in phase3.semantic_features(question) if key not in GENERIC_CONCEPTS}
    candidates = {}
    for row in rows:
        require(isinstance(row["text"], str) and len(row["text"]) <= 6400, "LAB_CONTENT_LIMIT")
        words = {word: 1 for word in phase3.lexical_features(row["text"]) if word not in STOP_WORDS}
        # Caller verifies the canonical module/graph join before using this helper.
        context = row.get("module_id", "").replace("-", " ")
        semantic = {key: 1 for key in phase3.semantic_features(row["text"]+"\n"+context)
                    if key not in GENERIC_CONCEPTS}
        lexical_score, semantic_score = phase3.cosine(tokens, words), phase3.cosine(concepts, semantic)
        # Common words, generic concepts and repetition cannot manufacture relevance.
        if not set(tokens) & set(words) and not set(concepts) & set(semantic):
            continue
        score = {"lexical": lexical_score, "semantic": semantic_score,
                 "hybrid": 0.4*lexical_score+0.6*semantic_score}[mode]
        if score <= 0:
            continue
        identity = citation_id(row)
        candidates[identity] = {"row": row, "citation_id": identity, "score": round(score, 6),
                                "lexical_score": round(lexical_score, 6),
                                "semantic_score": round(semantic_score, 6)}
    return sorted(candidates.values(), key=lambda item: (-item["score"], item["citation_id"]))

def select_claims(question, rows, required_claims, mode="hybrid"):
    require(isinstance(required_claims, list) and 1 <= len(required_claims) <= MAX_CITATIONS
            and len(set(required_claims)) == len(required_claims), "INVALID_LAB_REQUIRED_CLAIMS")
    stances = {}
    for row in rows:
        stances.setdefault(row["claim_key"], set()).add(row["stance"])
    require(not any(len(value) > 1 for value in stances.values()), "CONTRADICTORY_CURATED_CLAIMS_REQUIRE_REVIEW")
    ranked = meaningful_rank(question, rows, mode)
    selected = []
    for claim in required_claims:
        matches = [item for item in ranked if item["row"]["claim_key"] == claim]
        require(matches, "INSUFFICIENT_RELEVANT_CLAIM_COVERAGE")
        selected.append(matches[0])
    return selected

def retrieve(graph_path, index, request, *, root=clinical.ROOT):
    result = phase3.retrieve(graph_path, index, request, root=root)
    if result["status"] != "EXTRACTIVE_CONTENT":
        return result
    try:
        manifest = clinical.load_manifest(root)
        question = next(item for item in manifest["questions"] if item["id"] == result["question_id"])
        rows = clinical._select(index, question, clinical._date(request["as_of"]))
        selected = select_claims(question["question"], rows, question["required_claims"], request.get("mode", "hybrid"))
        result["citations"] = [dict(clinical._citation(item["row"]), citation_id=item["citation_id"],
                                    claim_key=item["row"]["claim_key"]) for item in selected]
        result["answer"] = "\n\n".join(item["quote"] for item in result["citations"])
        result["ranking"] = [{key: item[key] for key in ("citation_id", "score", "lexical_score", "semantic_score")}
                             for item in selected]
        result.update(retrieval_phase=4,
                      relevance_method="binary_content_terms_specific_concepts_and_verified_module_context",
                      required_claims=question["required_claims"], covered_claims=[item["row"]["claim_key"] for item in selected],
                      generation_performed=False, runtime_activation_authorized=False)
        return result
    except (OSError, ValueError, KeyError, TypeError, StopIteration, RecursionError) as error:
        return phase3._abstain(str(error) if isinstance(error, LabRejected) else "INVALID_LAB_RETRIEVAL_INPUT")

def _fixture_row(document, text, claim, stance="yes"):
    return {"document_id": document, "version": "invented-nonclinical-fixture-v1",
            "path": "synthetic-fixture:"+document, "source_sha256": sha(text.encode("utf8")),
            "line_start": 1, "line_end": 1, "text": text, "claim_key": claim, "stance": stance}

def fixture_case(case_id):
    require(case_id in {"supported", "insufficient", "contradiction"}, "UNKNOWN_SYNTHETIC_LAB_CASE")
    rows = [_fixture_row("amber", "The amber marker is square.", "amber-shape"),
            _fixture_row("violet", "The violet marker is round.", "violet-shape")]
    if case_id == "insufficient":
        rows.pop()
    if case_id == "contradiction":
        rows.append(_fixture_row("opposed", "The amber marker is not square.", "amber-shape", "no"))
    return {"case_id": case_id, "question": "Which shapes do the amber and violet markers have?",
            "required_claims": ["amber-shape", "violet-shape"], "rows": rows}

def prepare_fixture_request(case_id):
    case = fixture_case(case_id)
    selected = select_claims(case["question"], case["rows"], case["required_claims"])
    citations = []
    for item in selected:
        row = item["row"]
        citations.append({"citation_id": item["citation_id"], "claim_key": row["claim_key"],
                          "quote": row["text"], **{key: row[key] for key in (
                              "document_id", "version", "path", "source_sha256", "line_start", "line_end")}})
    return {"schema": "nonclinical-fixture-response-request-v1", "case_id": case_id,
            "synthetic_nonclinical_only": True, "document_role": "untrusted_data_not_instructions",
            "clinical_generation_authorized": False, "tools": [], "citations": citations}

class FixtureProvider:
    """Injectable deterministic fixture, never a model or an external transport."""
    def __init__(self, response=None):
        self.response = deepcopy(response)
        self.calls = 0

    def complete(self, request):
        self.calls += 1
        return ({"case_id": request["case_id"], "citations": deepcopy(request["citations"])}
                if self.response is None else deepcopy(self.response))

def validate_response(request, response):
    require(type(response) is dict and set(response) == {"case_id", "citations"},
            "INVALID_FIXTURE_OUTPUT_SHAPE")
    require(len(canonical(response)) <= MAX_LAB_BYTES, "FIXTURE_OUTPUT_LIMIT")
    require(response["case_id"] == request["case_id"], "FIXTURE_CASE_MISMATCH")
    entries = response["citations"]
    require(type(entries) is list and len(entries) == len(request["citations"]), "FIXTURE_CLAIM_COVERAGE_MISMATCH")
    expected = {item["citation_id"]: item for item in request["citations"]}
    seen = set()
    for item in entries:
        require(type(item) is dict and isinstance(item.get("citation_id"), str), "INVALID_FIXTURE_CITATION")
        key = item["citation_id"]
        require(key in expected and key not in seen and item == expected[key], "FIXTURE_CITATION_CONTENT_OR_PROVENANCE_MISMATCH")
        seen.add(key)
    require(seen == set(expected), "FIXTURE_CLAIM_COVERAGE_MISMATCH")
    return deepcopy(request["citations"])

def run_fixture_lab(case_id, *, provider=None, allow_fixture_response=False):
    denied = {"status": "ABSTAIN", "reason": "FIXTURE_RESPONSE_DISABLED", "fixture_provider_called": False,
              "fixture_calls_this_operation": 0,
              "generation_performed": False, "clinical_generation_authorized": False,
              "network_used": False, "actual_LLM_calls": 0, "provider_tokens_measured": None,
              "provider_cost_measured_usd": None, "clinical": "CLINICALLY_PENDING",
              "release": "NO_GO_CLINICAL_RELEASE", "corpus_scope": "LOCAL_ONLY"}
    try:
        require(type(allow_fixture_response) is bool, "INVALID_FIXTURE_PERMISSION")
        if not allow_fixture_response:
            return denied
        request = prepare_fixture_request(case_id)
        provider = FixtureProvider() if provider is None else provider
        require(type(provider) is FixtureProvider, "UNREVIEWED_PROVIDER_OR_EXTERNAL_TRANSPORT_DISABLED")
        start = time.perf_counter()
        denied["fixture_provider_called"] = True
        denied["fixture_calls_this_operation"] = 1
        response = provider.complete(deepcopy(request))
        latency = round((time.perf_counter()-start)*1000, 3)
        citations = validate_response(request, response)
        return {**denied, "status": "LAB_FIXTURE_RESPONSE_VALIDATED", "reason": None,
                "answer_mode": "validated_nonclinical_fixture_quotes_not_LLM",
                "citations": citations, "request_sha256": sha(canonical(request)),
                "response_sha256": sha(canonical(response)), "measured_fixture_latency_ms": latency,
                "fixture_calls_this_operation": 1}
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
        denied["reason"] = str(error) if isinstance(error, LabRejected) else "INVALID_FIXTURE_LAB_INPUT"
        return denied

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("supported", "insufficient", "contradiction"), default="supported")
    parser.add_argument("--allow-fixture-response", action="store_true")
    args = parser.parse_args(argv)
    result = run_fixture_lab(args.case, allow_fixture_response=args.allow_fixture_response)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "ABSTAIN" else 0

if __name__ == "__main__":
    raise SystemExit(main())
