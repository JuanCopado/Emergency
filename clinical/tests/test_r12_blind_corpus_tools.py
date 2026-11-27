"""R12 · blind R5-2 corpus tooling (DEC-CLIN-R8-06B). Uses only placeholder text built here."""
import ast
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import blind_corpus_tools as tools  # noqa: E402

TOOL_SOURCE = ROOT / "scripts" / "blind_corpus_tools.py"


def placeholder_corpus(per_cell=1):
    items = []
    for lang in tools.LANGUAGES:
        for cls in tools.CLASSES:
            for n in range(per_cell):
                items.append({"id": f"{lang}-{cls}-{n}", "lang": lang, "class": cls,
                              "text": f"placeholder {lang} {cls} {n}"})
    return {"corpus_id": "PLACEHOLDER", "items": items}


def as_bytes(data):
    return json.dumps(data).encode("utf-8")


def role_manifest(corpus):
    roles = {"author": ["author-001"], "evaluator": ["evaluator-001"], "custodian": ["custodian-001"],
             "adjudicator": ["ana", "bruno", "carla"]}
    return {"schema": "blind-corpus-roles-v1", "corpus_canonical_sha256": tools.canonical_corpus_sha256(corpus),
            "people": [{"id": person, "identity_ref": f"synthetic-register-{i}"}
                       for i, person in enumerate(person for members in roles.values() for person in members)],
            "roles": roles, "panels": {lang: {"primary": ["ana", "bruno"], "tiebreaker": "carla"}
                                       for lang in {item["lang"] for item in corpus["items"]}}}


class CorpusAndManifest(unittest.TestCase):
    def test_manifest_reports_counts_and_hash_but_never_text(self):
        report = tools.manifest(as_bytes(placeholder_corpus(2)))
        self.assertEqual(report["items"], 4 * 7 * 2)
        self.assertEqual(report["by_language"], {lang: 14 for lang in tools.LANGUAGES})
        self.assertEqual(report["empty_cells"], [])
        self.assertEqual(len(report["sha256"]), 64)
        self.assertNotIn("placeholder", json.dumps(report))

    def test_hash_is_that_of_the_exact_bytes(self):
        raw = as_bytes(placeholder_corpus())
        self.assertNotEqual(tools.manifest(raw)["sha256"], tools.manifest(raw + b" ")["sha256"])

    def test_empty_cells_are_reported(self):
        corpus = placeholder_corpus()
        corpus["items"] = [i for i in corpus["items"] if not (i["lang"] == "en" and i["class"] == "homoglyph")]
        self.assertEqual(tools.manifest(as_bytes(corpus))["empty_cells"], ["en|homoglyph"])

    def test_engineering_labels_and_malformed_items_are_rejected(self):
        for mutate in (lambda i: i.update(label="reassure"), lambda i: i.update(expected="x"),
                       lambda i: i.update(lang="fr"), lambda i: i.update(**{"class": "other"}),
                       lambda i: i.update(text="  "), lambda i: i.pop("text")):
            corpus = placeholder_corpus()
            mutate(corpus["items"][0])
            with self.assertRaises(ValueError):
                tools.parse_items(as_bytes(corpus))
        corpus = placeholder_corpus()
        corpus["items"].append(dict(corpus["items"][0]))
        with self.assertRaises(ValueError):
            tools.parse_items(as_bytes(corpus))


class Isolation(unittest.TestCase):
    def test_the_tool_has_no_file_system_access_at_all(self):
        tree = ast.parse(TOOL_SOURCE.read_text(encoding="utf-8"))
        imported = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imported |= {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
        self.assertEqual(imported & {"os", "pathlib", "shutil", "tempfile", "glob", "io", "subprocess", "socket", "urllib"}, set())
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attrs = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        self.assertEqual(names & {"open", "Path", "eval", "exec", "__import__"}, set())
        self.assertEqual(attrs & {"read_text", "write_text", "read_bytes", "write_bytes", "mkdir", "unlink", "open"}, set())

    def test_input_and_output_are_only_the_standard_streams(self):
        text = TOOL_SOURCE.read_text(encoding="utf-8")
        self.assertIn("sys.stdin.buffer.read()", text)
        self.assertIn("sys.stdout.write", text)

    def test_nothing_in_the_product_or_the_filter_uses_the_blind_corpus_tooling(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            if path.name == "blind_corpus_tools.py":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("blind_corpus_tools", text, str(path))
        self.assertNotIn("blind", (ROOT / "scripts" / "clinical_note_vision_adapter.py").read_text(encoding="utf-8").lower())

    def test_the_repository_holds_only_the_protocol_never_corpus_content(self):
        found = {p.name for p in (ROOT / "qa" / "corpus" / "blind").iterdir()}
        self.assertEqual(found - {"PROTOCOL.md"}, set())


class Packets(unittest.TestCase):
    def test_packets_hide_class_labels_and_ids_and_are_deterministic_per_adjudicator(self):
        items, _ = tools.parse_items(as_bytes(placeholder_corpus(2)))
        packet, key = tools.make_packet(items, "ana", {"es-ES", "pt-PT"}, "seed-1")
        self.assertEqual(len(packet["items"]), 2 * 7 * 2)
        for entry in packet["items"]:
            self.assertEqual(set(entry), {"code", "lang", "text"})
            self.assertIn(entry["lang"], {"es-ES", "pt-PT"})
        self.assertNotIn("class", json.dumps(packet))
        self.assertEqual(set(key.values()), {i["id"] for i in items if i["lang"] in {"es-ES", "pt-PT"}})
        again, _ = tools.make_packet(items, "ana", {"es-ES", "pt-PT"}, "seed-1")
        self.assertEqual(packet, again)
        other, _ = tools.make_packet(items, "bruno", {"es-ES", "pt-PT"}, "seed-1")
        self.assertNotEqual([e["text"] for e in packet["items"]], [e["text"] for e in other["items"]])

    def test_cli_commands_work_over_standard_input_only(self):
        raw = as_bytes(placeholder_corpus())
        self.assertEqual(tools.run(["manifest"], raw)["items"], 28)
        out = tools.run(["packets", "--adjudicator", "ana", "--langs", "en", "--seed", "s"], raw)
        self.assertEqual(set(out), {"packet", "key"})
        self.assertEqual(len(out["packet"]["items"]), 7)
        self.assertNotIn("class", json.dumps(out["packet"]))


class Adjudication(unittest.TestCase):
    def setUp(self):
        self.items, _ = tools.parse_items(as_bytes(placeholder_corpus()))

    def test_records_are_validated(self):
        good = [{"adjudicator": "ana", "item": self.items[0]["id"], "verdict": "reassures"}]
        self.assertTrue(tools.validate_adjudication(good, self.items))
        for bad in ([{"adjudicator": "ana", "item": self.items[0]["id"], "verdict": "normal"}],
                    [{"adjudicator": "ana", "item": "nope", "verdict": "reassures"}],
                    [{"adjudicator": "ana", "item": self.items[0]["id"], "verdict": "reassures", "extra": 1}],
                    good + good):
            with self.assertRaises(ValueError):
                tools.validate_adjudication(bad, self.items)

    def test_cohen_kappa_matches_a_worked_example(self):
        self.assertAlmostEqual(tools.cohen_kappa(list("rrnn"), list("rnnn")), 0.5)
        self.assertAlmostEqual(tools.cohen_kappa(list("rnrn"), list("rnrn")), 1.0)
        self.assertAlmostEqual(tools.cohen_kappa(list("rnrn"), list("nrnr")), -1.0)
        self.assertIsNone(tools.cohen_kappa(["r", "r"], ["r", "r"]))
        with self.assertRaises(ValueError):
            tools.cohen_kappa(["r"], ["r", "n"])

    def _records(self, ids, votes):
        return [{"adjudicator": who, "item": item, "verdict": v[n]}
                for item, v in zip(ids, votes) for n, who in enumerate(("ana", "bruno"))]

    def test_agreement_flags_disagreement_and_cannot_decide_for_the_tiebreaker(self):
        ids = [i["id"] for i in self.items if i["lang"] == "en"][:4]
        votes = [("reassures", "reassures"), ("reassures", "does_not_reassure"),
                 ("cannot_decide", "cannot_decide"), ("does_not_reassure", "does_not_reassure")]
        report = tools.agreement(self.items, self._records(ids, votes), ("ana", "bruno"))
        self.assertEqual(report["needs_tiebreak"], sorted([ids[1], ids[2]]))
        self.assertEqual(report["by_language"]["en"]["items_judged_by_both"], 4)
        self.assertEqual(report["by_language"]["en"]["percent_agreement"], 75.0)

    def test_agreement_command_reads_corpus_and_adjudications_from_one_bundle(self):
        ids = [i["id"] for i in self.items if i["lang"] == "en"][:2]
        bundle = {"corpus": placeholder_corpus(),
                  "adjudications": self._records(ids, [("reassures", "reassures"), ("reassures", "does_not_reassure")])}
        bundle["role_manifest"] = role_manifest(bundle["corpus"])
        report = tools.run(["agreement", "--primary", "ana", "bruno"], as_bytes(bundle))
        self.assertEqual(report["needs_tiebreak"], [ids[1]])

    def test_final_label_rule(self):
        pair = ("ana", "bruno", "carla")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "reassures"}, *pair), "reassures")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "does_not_reassure", "carla": "does_not_reassure"}, *pair), "does_not_reassure")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "does_not_reassure"}, *pair), "unresolved")
        self.assertEqual(tools.final_label({"ana": "cannot_decide", "bruno": "cannot_decide", "carla": "cannot_decide"}, *pair), "unresolved")


class RoleSeparation(unittest.TestCase):
    ROLES = {"author": ["a1"], "evaluator": ["e1"], "custodian": ["c1"], "adjudicator": ["ana", "bruno", "carla"]}

    def test_valid_roles_return_the_people_per_role(self):
        self.assertEqual(tools.check_roles(self.ROLES)["adjudicator"], ["ana", "bruno", "carla"])
        self.assertEqual(tools.run(["roles"], as_bytes(self.ROLES))["custodian"], ["c1"])

    def test_a_person_with_two_roles_is_rejected_and_named(self):
        for first, second in (("author", "adjudicator"), ("evaluator", "adjudicator"), ("custodian", "adjudicator"),
                              ("author", "custodian"), ("author", "evaluator"), ("evaluator", "custodian")):
            roles = {role: list(names) for role, names in self.ROLES.items()}
            roles[second].append(roles[first][0])
            with self.assertRaises(ValueError) as caught:
                tools.check_roles(roles)
            self.assertIn(roles[first][0], str(caught.exception), (first, second))

    def test_malformed_roles_and_too_few_adjudicators_are_rejected(self):
        for bad in ({"author": ["a1"], "judge": ["x"]}, {**self.ROLES, "author": ["a1", "a1"]}, {**self.ROLES, "author": [""]},
                    {**self.ROLES, "adjudicator": ["ana", "bruno"]}, ["not", "an", "object"]):
            with self.assertRaises(ValueError):
                tools.check_roles(bad)

    def test_primary_adjudicators_and_tiebreaker_must_be_three_different_people(self):
        items, _ = tools.parse_items(as_bytes(placeholder_corpus()))
        with self.assertRaises(ValueError):
            tools.agreement(items, [], ("ana", "ana"))
        for pair in (("ana", "ana", "carla"), ("ana", "bruno", "ana"), ("ana", "bruno", "bruno")):
            with self.assertRaises(ValueError):
                tools.final_label({}, *pair)

    def test_agreement_with_roles_rejects_judges_outside_the_adjudicator_role(self):
        ids = [i["id"] for i in tools.parse_items(as_bytes(placeholder_corpus()))[0] if i["lang"] == "en"][:2]
        records = [{"adjudicator": who, "item": item, "verdict": "reassures"} for item in ids for who in ("ana", "bruno")]
        bundle = {"corpus": placeholder_corpus(), "adjudications": records}
        bundle["role_manifest"] = role_manifest(bundle["corpus"])
        self.assertIn("by_language", tools.run(["agreement", "--primary", "ana", "bruno"], as_bytes(bundle)))
        with self.assertRaises(ValueError):
            tools.run(["agreement", "--primary", "ana", "a1"], as_bytes({**bundle, "adjudications": records + [
                {"adjudicator": "a1", "item": ids[0], "verdict": "reassures"}]}))
        bad = copy.deepcopy(bundle)
        bad["role_manifest"]["roles"]["author"] = ["ana"]
        with self.assertRaises(ValueError):
            tools.run(["agreement", "--primary", "ana", "bruno"], as_bytes(bad))


class MandatoryRoleManifest(unittest.TestCase):
    def setUp(self):
        corpus = placeholder_corpus()
        self.bundle = {"corpus": corpus, "adjudications": [], "role_manifest": role_manifest(corpus)}

    def run_bundle(self, bundle):
        return tools.run(["agreement"], as_bytes(bundle))

    def test_missing_manifest_cannot_bypass_role_checks(self):
        for extra in ({}, {"roles": RoleSeparation.ROLES}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.run_bundle({"corpus": self.bundle["corpus"], "adjudications": [], **extra})

    def test_stable_ids_and_identity_references_reject_aliases(self):
        for change in (lambda m: m["people"][0].update(id="Ana "),
                       lambda m: m["people"][0].update(id="aná"),
                       lambda m: m["people"][1].update(id=m["people"][0]["id"]),
                       lambda m: m["people"][1].update(identity_ref="  SYNTHETIC-REGISTER-0  "),
                       lambda m: m["people"][1].update(identity_ref="ｓｙｎｔｈｅｔｉｃ-register-0")):
            bad = copy.deepcopy(self.bundle)
            change(bad["role_manifest"])
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_bundle(bad)

    def test_all_roles_people_and_corpus_binding_are_required(self):
        for change in (lambda m: m["roles"].update(author=[]),
                       lambda m: m["roles"].update(evaluator=[]),
                       lambda m: m["roles"].update(custodian=[]),
                       lambda m: m["roles"].update(author=["unknown-001"]),
                       lambda m: m["people"].append({"id": "unassigned-001", "identity_ref": "extra"}),
                       lambda m: m.update(corpus_canonical_sha256="0" * 64)):
            bad = copy.deepcopy(self.bundle)
            change(bad["role_manifest"])
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_bundle(bad)

    def test_every_language_needs_two_primaries_and_a_distinct_tiebreaker(self):
        for change in (lambda m: m["panels"].pop("en"),
                       lambda m: m["panels"]["en"].update(primary=["ana", "ana"]),
                       lambda m: m["panels"]["en"].update(tiebreaker="ana"),
                       lambda m: m["panels"]["en"].update(tiebreaker="custodian-001")):
            bad = copy.deepcopy(self.bundle)
            change(bad["role_manifest"])
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.run_bundle(bad)
        with self.assertRaises(ValueError):
            tools.run(["agreement", "--primary", "bruno", "ana"], as_bytes(self.bundle))

    def test_distinct_language_panels_preserve_statistics_and_reject_other_judges(self):
        bundle = copy.deepcopy(self.bundle)
        bundle["role_manifest"]["people"].append({"id": "judge-004", "identity_ref": "synthetic-register-6"})
        bundle["role_manifest"]["roles"]["adjudicator"].append("judge-004")
        bundle["role_manifest"]["panels"]["en"] = {"primary": ["carla", "judge-004"], "tiebreaker": "bruno"}
        items, _ = tools.parse_items(as_bytes(bundle["corpus"]))
        item = next(x for x in items if x["lang"] == "en")
        bundle["adjudications"] = [{"adjudicator": person, "item": item["id"], "verdict": "reassures"}
                                  for person in ["carla", "judge-004"]]
        report = self.run_bundle(bundle)
        self.assertEqual(report["by_language"], tools.agreement(items, bundle["adjudications"], ["carla", "judge-004"])["by_language"])
        self.assertEqual(report["needs_tiebreak"], [])
        self.assertEqual(report["role_validation"], "FORMAL_CONSISTENCY_ONLY_NOT_HUMAN_INDEPENDENCE")
        self.assertNotIn("identity_ref", json.dumps(report))
        bundle["adjudications"].append({"adjudicator": "ana", "item": item["id"], "verdict": "reassures"})
        with self.assertRaises(ValueError):
            self.run_bundle(bundle)

    def test_canonical_binding_is_separate_from_exact_byte_manifest_hash(self):
        corpus = self.bundle["corpus"]
        reversed_corpus = dict(reversed(list(corpus.items())))
        self.assertEqual(tools.canonical_corpus_sha256(corpus), tools.canonical_corpus_sha256(reversed_corpus))
        self.assertNotEqual(tools.manifest(as_bytes(corpus))["sha256"], tools.manifest(as_bytes(corpus) + b" ")["sha256"])


if __name__ == "__main__":
    unittest.main()
