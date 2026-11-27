"""Bounded offline hybrid ranking and scientific-query laboratory.

Semantic features are a small explicit multilingual concept dictionary, not a
trained embedding model. Only the predeclared synthetic questions are admitted.
Phase2 remains the authority for permissions, integrity, joins and abstention.
"""
from __future__ import annotations

import argparse
from collections import Counter
import html
import json
import math
import re
import time
from typing import Protocol

from cli_paths import input_file, output_file
import rag_clinical_extracts as clinical

CONCEPT_VERSION = "emergency-local-concepts-v1"
CONCEPTS = {
    "electrocardiogram": ("ecg", "electrocardiogram", "electrocardiograma"),
    "troponin": ("troponin", "troponina"),
    "acs": ("acs", "acute coronary syndrome", "síndrome coronario agudo", "sca"),
    "assessment": ("assessment", "evaluación", "valorar", "evaluar", "valoración"),
    "potassium": ("hyperkalemia", "hiperpotasemia", "potassium", "potasio"),
    "adrenal": ("adrenal", "suprarrenal"),
    "normal": ("normal",),
}
MODES = {"lexical", "semantic", "hybrid"}
MAX_UI_BYTES = 131072


def lexical_features(text):
    return Counter(re.findall(r"[^\W_]+", text.casefold(), re.UNICODE))


def semantic_features(text):
    # Boundaries prevent accidental matches such as 'sca' inside another word.
    folded = text.casefold()
    return Counter({concept: 1 for concept, aliases in CONCEPTS.items()
                    if any(re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", folded)
                           for alias in aliases)})


class SemanticEncoder(Protocol):
    """Trusted-code encoder interface; never loaded from a request/document."""

    name: str

    def encode(self, text: str) -> Counter: ...


class ConceptEncoder:
    name = CONCEPT_VERSION

    def encode(self, text):
        return semantic_features(text)


def cosine(left, right):
    numerator = sum(value * right.get(key, 0) for key, value in left.items())
    denominator = math.sqrt(sum(v * v for v in left.values()) * sum(v * v for v in right.values()))
    return numerator / denominator if denominator else 0.0


def rank_rows(question, rows, mode, *, encoder: SemanticEncoder | None = None):
    if mode not in MODES:
        raise ValueError("UNSUPPORTED_RETRIEVAL_MODE")
    encoder = encoder or ConceptEncoder()
    lexical, semantic = lexical_features(question), encoder.encode(question)
    ranked = []
    for row in rows:
        lx = cosine(lexical, lexical_features(row["text"]))
        sm = cosine(semantic, encoder.encode(row["text"]))
        score = {"lexical": lx, "semantic": sm, "hybrid": 0.4 * lx + 0.6 * sm}[mode]
        ranked.append((score, row["document_id"], row["line_start"], row, lx, sm))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [{"row": row, "score": round(score, 6), "lexical": round(lx, 6),
             "semantic": round(sm, 6)} for score, _, _, row, lx, sm in ranked]


def _abstain(reason):
    result = clinical._result(reason)
    result.update(retrieval_phase=3, corpus_scope="LOCAL_ONLY")
    return result


def retrieve(graph_path, index, request, *, root=clinical.ROOT):
    """Question IDs, not patient free text. Ranking can never override a gate."""
    started = time.perf_counter()
    try:
        if (not isinstance(request, dict) or set(request) - {"synthetic", "question_id", "as_of", "mode"}
                or request.get("synthetic") is not True):
            return _abstain("INVALID_SYNTHETIC_REQUEST")
        manifest = clinical.load_manifest(root)
        questions = [item for item in manifest["questions"] if item["id"] == request.get("question_id")]
        if len(questions) != 1 or request.get("mode", "hybrid") not in MODES:
            return _abstain("QUESTION_OR_MODE_OUTSIDE_AUTHORIZED_SCOPE")
        question = questions[0]
        query = {"synthetic": True, "question": question["question"], "as_of": request.get("as_of")}
        result = clinical.retrieve_extracts(graph_path, index, query, root=root)
        if result["status"] != "EXTRACTIVE_CONTENT":
            return result
        # The existing gate verifies the whole index against original source and
        # graph bytes; never rank supplied text before that succeeds.
        evaluated = clinical._date(request["as_of"])
        rows = clinical._select(index, question, evaluated)
        ranked = rank_rows(question["question"], rows, request.get("mode", "hybrid"))
        result["citations"] = [clinical._citation(item["row"]) for item in ranked]
        result["answer"] = "\n\n".join(item["quote"] for item in result["citations"])
        result["ranking"] = [{"document_id": item["row"]["document_id"],
                              "line_start": item["row"]["line_start"],
                              "score": item["score"], "lexical_score": item["lexical"],
                              "semantic_score": item["semantic"]} for item in ranked]
        result.update(retrieval_phase=3, retrieval_mode=request.get("mode", "hybrid"),
                      semantic_method="explicit_multilingual_concepts_not_trained_embeddings",
                      semantic_version=CONCEPT_VERSION,
                      contradiction_method="opposed_curated_stances_same_claim_key_not_general_NLI",
                      measured_retrieval_latency_ms=round((time.perf_counter() - started) * 1000, 3))
        return result
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        return _abstain("INVALID_OR_UNAVAILABLE_PHASE3_INPUT")


def render_ui(graph_path, index, as_of, *, root=clinical.ROOT):
    """Read-only offline query interface: native details controls, no JS/network.

    Outputs contain authorized quotes and must remain LOCAL_ONLY. Dynamic text
    is HTML escaped; sources never become active links or executable markup.
    """
    manifest = clinical.load_manifest(root)
    panels = []
    for question in manifest["questions"]:
        result = retrieve(graph_path, index, {"synthetic": True, "question_id": question["id"],
                          "as_of": as_of, "mode": "hybrid"}, root=root)
        citations = []
        for citation in result["citations"]:
            label = f'{citation["document_id"]} · {citation["version"]} · {citation["path"]}:{citation["line_start"]}–{citation["line_end"]}'
            # quote is already inert escaped text, but escape again as ordinary
            # visible data to avoid decoding any source markup at the UI boundary.
            citations.append("<p>" + html.escape(label) + "</p><pre>" + html.escape(citation["quote"]) + "</pre>")
        panels.append("<details><summary>" + html.escape(question["question"]) + "</summary><p>" +
                      html.escape(result["status"] + " · " + (result["reason"] or "Síntesis propia; no evidencia primaria")) +
                      "</p>" + "".join(citations) + "</details>")
    page = ('<!doctype html><html lang="es"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'">'
            '<meta name="referrer" content="no-referrer"><title>Visor experimental de consultas sintéticas — Emergency</title>'
            '<body><main><h1>Visor experimental de consultas sintéticas</h1>'
            '<p>Resultados calculados al generar este archivo. Los desplegables no ejecutan consultas nuevas.</p>'
            '<p>Solo preguntas sintéticas predefinidas. Sin entrada de pacientes, generación, red ni prescripción.</p>'
            '<p>Recuperación híbrida local por conceptos explícitos; no embeddings entrenados. '
            'CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE · LOCAL_ONLY</p>' + "".join(panels) + '</main></body></html>')
    if len(page.encode("utf-8")) > MAX_UI_BYTES:
        raise ValueError("UI_SIZE_LIMIT")
    return page


def main(argv=None, *, root=clinical.ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("retrieve", "ui"))
    parser.add_argument("--graph", required=True, type=input_file)
    parser.add_argument("--index", required=True, type=input_file)
    parser.add_argument("--query", type=input_file)
    parser.add_argument("--as-of")
    parser.add_argument("--output", type=output_file)
    args = parser.parse_args(argv)
    try:
        if args.index.stat().st_size > clinical.MAX_INDEX_BYTES:
            raise ValueError("INDEX_SIZE_LIMIT")
        index = json.loads(args.index.read_text(encoding="utf-8"))
        if args.operation == "ui":
            if args.output is None:
                raise ValueError("OUTPUT_REQUIRED")
            page = render_ui(args.graph, index, args.as_of, root=root)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(page, encoding="utf-8")
            result = {"status": "UI_PREPARED", "corpus_scope": "LOCAL_ONLY", "network_used": False}
        else:
            if args.query is None or args.query.stat().st_size > 2048:
                raise ValueError("QUERY_SIZE_LIMIT")
            result = retrieve(args.graph, index, json.loads(args.query.read_text(encoding="utf-8")), root=root)
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        result = _abstain("INVALID_OR_UNAVAILABLE_PHASE3_INPUT")
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 2 if result["status"] == "ABSTAIN" else 0


if __name__ == "__main__":
    raise SystemExit(main())
