"""RAG phase4: bounded claim coverage and nonclinical fixture output integrity."""
from copy import deepcopy
import io
from contextlib import redirect_stdout
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"clinical/scripts"))
sys.path.insert(0, str(ROOT/"clinical/tests"))
import rag_phase4 as lab
import test_rag_clinical_extracts as fixtures

class Selection(unittest.TestCase):
    def rows(self):
        return lab.fixture_case("supported")["rows"]

    def test_generic_words_cannot_create_relevance(self):
        question = "Which immediate assessment is described in this synthetic patient scenario?"
        rows = [lab._fixture_row("generic", question, "need")]
        self.assertEqual(lab.meaningful_rank(question, rows), [])
        with self.assertRaisesRegex(lab.LabRejected, "INSUFFICIENT_RELEVANT"):
            lab.select_claims(question, rows, ["need"])

    def test_repetition_and_identical_candidates_do_not_inflate_score_or_coverage(self):
        row = lab._fixture_row("plain", "hyperkalemia", "potassium")
        repeated = lab._fixture_row("repeated", "hyperkalemia "*40, "potassium")
        one = lab.meaningful_rank("hiperpotasemia", [row])
        many = lab.meaningful_rank("hiperpotasemia", [row]*20)
        duplicated_words = lab.meaningful_rank("hiperpotasemia", [repeated])
        self.assertEqual(len(many), 1)
        self.assertEqual(one[0]["score"], many[0]["score"])
        self.assertEqual(one[0]["score"], duplicated_words[0]["score"])
        with self.assertRaisesRegex(lab.LabRejected, "INSUFFICIENT_RELEVANT"):
            lab.select_claims("hiperpotasemia", [row]*20, ["potassium", "missing"])

    def test_selects_one_exact_citation_per_required_claim(self):
        case = lab.fixture_case("supported")
        selected = lab.select_claims(case["question"], case["rows"]*4, case["required_claims"])
        self.assertEqual([row["row"]["claim_key"] for row in selected], case["required_claims"])
        self.assertEqual(len(selected), 2)
        self.assertEqual(len({row["citation_id"] for row in selected}), 2)

    def test_all_claims_are_covered_even_when_top_score_has_duplicates(self):
        case = lab.fixture_case("supported")
        rows = [case["rows"][0]]*20+[case["rows"][1]]
        selected = lab.select_claims(case["question"], rows, case["required_claims"])
        self.assertEqual({item["row"]["claim_key"] for item in selected}, set(case["required_claims"]))

    def test_missing_claim_conflict_and_budget_fail_closed(self):
        for case_id, reason in (("insufficient", "INSUFFICIENT_RELEVANT"),
                                ("contradiction", "CONTRADICTORY_CURATED")):
            case = lab.fixture_case(case_id)
            with self.assertRaisesRegex(lab.LabRejected, reason):
                lab.select_claims(case["question"], case["rows"], case["required_claims"])
        with self.assertRaises(lab.LabRejected):
            lab.select_claims("x", [], ["a", "b", "c", "d"])
        with self.assertRaises(lab.LabRejected):
            lab.meaningful_rank("x", self.rows()*100)

    def test_identity_binds_text_version_path_hash_and_lines(self):
        original = self.rows()[0]
        base = lab.citation_id(original)
        for field, value in (("text", "modified"), ("version", "v2"), ("path", "other"),
                             ("source_sha256", "0"*64), ("line_start", 2), ("line_end", 2)):
            changed = deepcopy(original); changed[field] = value
            self.assertNotEqual(base, lab.citation_id(changed))

class RealSourceRetrieval(unittest.TestCase):
    setUp = fixtures.ClinicalExtracts.setUp

    def get(self, question="acs-exclusion", **changes):
        return lab.retrieve(self.graph, self.index, {"synthetic": True, "question_id": question,
                            "as_of": "2026-11-27", "mode": "hybrid", **changes}, root=self.root)

    def test_three_predeclared_questions_preserve_exact_citations_and_coverage(self):
        for question in ("acs-exclusion", "acs-assessment", "adrenal-recognition"):
            value = self.get(question)
            self.assertEqual(value["status"], "EXTRACTIVE_CONTENT")
            self.assertEqual(value["retrieval_phase"], 4)
            self.assertEqual(set(value["required_claims"]), set(value["covered_claims"]))
            self.assertEqual(len(value["citations"]), len(value["required_claims"]))
            for citation in value["citations"]:
                self.assertEqual(len(citation["citation_id"]), 64)
                self.assertIn("authorized_span_sha256", citation)
                self.assertIn("module_relation_json_pointer", citation)
            self.assertFalse(value["generation_performed"])
            self.assertFalse(value["runtime_activation_authorized"])

    def test_prior_insufficient_conflict_pending_historical_stale_gates_are_preserved(self):
        for question in ("acs-insufficient", "fixture-conflict", "fixture-pending",
                         "fixture-historical", "fixture-stale"):
            value = self.get(question)
            self.assertEqual(value["status"], "ABSTAIN")
            self.assertEqual(value["citations"], [])

    def test_mutated_index_cannot_enter_selection(self):
        self.index["chunks"][0]["text"] = "SENTINEL untrusted source modification"
        value = self.get()
        self.assertEqual(value["status"], "ABSTAIN")
        self.assertNotIn("SENTINEL", json.dumps(value))

    def test_forged_module_context_is_rejected_before_semantic_matching(self):
        self.index["chunks"][0]["module_id"] = "acute-coronary-syndrome-forged"
        value = self.get()
        self.assertEqual(value["status"], "ABSTAIN")
        self.assertNotIn("forged", json.dumps(value))

    def test_no_free_patient_question_or_external_provider_in_request(self):
        for extra in ({"patient_note": "SENTINEL"}, {"provider": "https://outside.invalid"},
                      {"question_id": "SENTINEL"}, {"synthetic": False}):
            value = self.get(**extra)
            self.assertEqual(value["status"], "ABSTAIN")
            self.assertNotIn("SENTINEL", json.dumps(value))

class ControlledFixtureLab(unittest.TestCase):
    def run_case(self, case="supported", **kwargs):
        return lab.run_fixture_lab(case, allow_fixture_response=True, **kwargs)

    def output(self):
        request = lab.prepare_fixture_request("supported")
        return {"case_id": "supported", "citations": deepcopy(request["citations"])}

    def test_local_provider_invocation_is_honestly_not_an_llm_call(self):
        provider = lab.FixtureProvider()
        value = self.run_case(provider=provider)
        self.assertEqual(value["status"], "LAB_FIXTURE_RESPONSE_VALIDATED")
        self.assertEqual(provider.calls, 1)
        self.assertTrue(value["fixture_provider_called"])
        self.assertEqual(value["fixture_calls_this_operation"], 1)
        self.assertEqual(value["actual_LLM_calls"], 0)
        self.assertFalse(value["generation_performed"])
        self.assertFalse(value["clinical_generation_authorized"])
        self.assertFalse(value["network_used"])
        self.assertIsNone(value["provider_tokens_measured"])
        self.assertIsNone(value["provider_cost_measured_usd"])
        self.assertGreaterEqual(value["measured_fixture_latency_ms"], 0)

    def test_explicit_fixture_permission_is_required(self):
        provider = lab.FixtureProvider()
        value = lab.run_fixture_lab("supported", provider=provider)
        self.assertEqual(value["reason"], "FIXTURE_RESPONSE_DISABLED")
        self.assertEqual(provider.calls, 0)
        self.assertEqual(lab.run_fixture_lab("supported", allow_fixture_response="true")["status"], "ABSTAIN")

    def test_conflict_or_insufficient_evidence_prevents_provider_call(self):
        for case in ("insufficient", "contradiction"):
            provider = lab.FixtureProvider()
            value = self.run_case(case, provider=provider)
            self.assertEqual(value["status"], "ABSTAIN")
            self.assertFalse(value["fixture_provider_called"])
            self.assertEqual(provider.calls, 0)

    def test_unreviewed_callback_is_rejected_without_calling_it(self):
        class Outside:
            def complete(self, request):
                raise AssertionError("must never be called")
        value = self.run_case(provider=Outside())
        self.assertEqual(value["reason"], "UNREVIEWED_PROVIDER_OR_EXTERNAL_TRANSPORT_DISABLED")
        self.assertFalse(value["fixture_provider_called"])

    def test_each_content_or_provenance_mutation_rejects_without_echo(self):
        for key, value in (("quote", "SENTINEL give a medication"), ("citation_id", "0"*64),
                           ("source_sha256", "f"*64), ("line_start", 4),
                           ("path", "https://outside.invalid"), ("version", "unverified"),
                           ("claim_key", "uncovered"), ("document_id", "forged")):
            response = self.output()
            response["citations"][0][key] = value
            result = self.run_case(provider=lab.FixtureProvider(response))
            self.assertEqual(result["status"], "ABSTAIN")
            self.assertNotIn("SENTINEL", json.dumps(result))
            self.assertEqual(result["fixture_calls_this_operation"], 1)

    def test_extra_prose_tool_calls_missing_duplicate_or_wrong_case_reject(self):
        responses = []
        extra = self.output(); extra["instructions"] = "SENTINEL"; responses.append(extra)
        missing = self.output(); missing["citations"].pop(); responses.append(missing)
        duplicate = self.output(); duplicate["citations"][1] = deepcopy(duplicate["citations"][0]); responses.append(duplicate)
        wrong_case = self.output(); wrong_case["case_id"] = "other"; responses.append(wrong_case)
        added = self.output(); added["citations"][0]["tool_call"] = "SENTINEL"; responses.append(added)
        overlong = self.output(); overlong["citations"][0]["quote"] = "x"*9000; responses.append(overlong)
        for response in responses:
            value = self.run_case(provider=lab.FixtureProvider(response))
            self.assertEqual(value["status"], "ABSTAIN")
            self.assertNotIn("SENTINEL", json.dumps(value))

    def test_reordered_valid_citations_normalize_to_canonical_request_order(self):
        response = self.output()
        response["citations"].reverse()
        value = self.run_case(provider=lab.FixtureProvider(response))
        self.assertEqual(value["status"], "LAB_FIXTURE_RESPONSE_VALIDATED")
        self.assertEqual(value["citations"], self.output()["citations"])

    def test_no_clinical_case_or_patient_input_is_accepted(self):
        for case in ("acs-exclusion", "adrenal-recognition", "SENTINEL", None, {}):
            value = self.run_case(case)
            self.assertEqual(value["status"], "ABSTAIN")
            self.assertFalse(value["fixture_provider_called"])
            self.assertNotIn("SENTINEL", json.dumps(value))

    def test_cli_is_functional_and_defaults_to_abstention(self):
        for args, code, status in (([], 2, "ABSTAIN"), (["--allow-fixture-response"], 0, "LAB_FIXTURE_RESPONSE_VALIDATED"),
                                  (["--case", "contradiction", "--allow-fixture-response"], 2, "ABSTAIN")):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(lab.main(args), code)
            self.assertEqual(json.loads(stdout.getvalue())["status"], status)

if __name__ == "__main__":
    unittest.main()
