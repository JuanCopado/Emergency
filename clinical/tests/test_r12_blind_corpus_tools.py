"""R12 · blind R5-2 corpus tooling (DEC-CLIN-R8-06B). Uses only placeholder text built here."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import blind_corpus_tools as tools  # noqa: E402


def placeholder_corpus(per_cell=1):
    items = []
    for lang in tools.LANGUAGES:
        for cls in tools.CLASSES:
            for n in range(per_cell):
                items.append({"id": f"{lang}-{cls}-{n}", "lang": lang, "class": cls,
                              "text": f"placeholder {lang} {cls} {n}"})
    return {"corpus_id": "PLACEHOLDER", "items": items}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, data):
        path = self.dir / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path


class CorpusAndManifest(Base):
    def test_manifest_reports_counts_and_hash_but_never_text(self):
        path = self.write("c.json", placeholder_corpus(2))
        report = tools.manifest(path)
        self.assertEqual(report["items"], 4 * 7 * 2)
        self.assertEqual(report["by_language"], {lang: 14 for lang in tools.LANGUAGES})
        self.assertEqual(report["empty_cells"], [])
        self.assertEqual(len(report["sha256"]), 64)
        self.assertNotIn("placeholder", json.dumps(report))

    def test_empty_cells_are_reported(self):
        corpus = placeholder_corpus()
        corpus["items"] = [i for i in corpus["items"] if not (i["lang"] == "en" and i["class"] == "homoglyph")]
        self.assertEqual(tools.manifest(self.write("c.json", corpus))["empty_cells"], ["en|homoglyph"])

    def test_engineering_labels_and_malformed_items_are_rejected(self):
        for mutate in (lambda i: i.update(label="reassure"), lambda i: i.update(expected="x"),
                       lambda i: i.update(lang="fr"), lambda i: i.update(**{"class": "other"}),
                       lambda i: i.update(text="  "), lambda i: i.pop("text")):
            corpus = placeholder_corpus()
            mutate(corpus["items"][0])
            with self.assertRaises(ValueError):
                tools.load_items(self.write("bad.json", corpus))
        corpus = placeholder_corpus()
        corpus["items"].append(dict(corpus["items"][0]))
        with self.assertRaises(ValueError):
            tools.load_items(self.write("dup.json", corpus))


class Isolation(Base):
    def test_every_path_inside_the_repository_is_refused(self):
        inside = ROOT / "qa" / "corpus" / "blind" / "should-not-exist.json"
        with self.assertRaises(SystemExit):
            tools.ensure_outside_repo(inside, "x")
        with self.assertRaises(SystemExit):
            tools.load_items(ROOT / "qa" / "corpus" / "r8_reassurance_synthetic_corpus_v0.json")
        corpus = self.write("c.json", placeholder_corpus())
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            tools.main(["packets", str(corpus), "--adjudicator", "a", "--langs", "en", "--seed", "1",
                        "--out", str(ROOT / "qa" / "corpus" / "blind")])
        self.assertFalse(inside.exists())

    def test_nothing_in_the_product_or_the_filter_uses_the_blind_corpus_tooling(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            if path.name == "blind_corpus_tools.py":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("blind_corpus_tools", text, str(path))
        self.assertNotIn("blind", (ROOT / "scripts" / "clinical_note_vision_adapter.py").read_text(encoding="utf-8").lower())

    def test_the_repository_holds_only_the_protocol_never_corpus_content(self):
        allowed = {"PROTOCOL.md"}
        found = {p.name for p in (ROOT / "qa" / "corpus" / "blind").iterdir()}
        self.assertEqual(found - allowed, set())


class Packets(Base):
    def test_packets_hide_class_labels_and_ids_and_are_deterministic_per_adjudicator(self):
        items, _ = tools.load_items(self.write("c.json", placeholder_corpus(2)))
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

    def test_cli_writes_packet_and_key_outside_the_repository(self):
        corpus = self.write("c.json", placeholder_corpus())
        out = self.dir / "out"
        with contextlib.redirect_stdout(io.StringIO()):
            tools.main(["packets", str(corpus), "--adjudicator", "ana", "--langs", "en", "--seed", "s", "--out", str(out)])
        self.assertTrue((out / "packet-ana.json").exists() and (out / "key-ana.json").exists())


class Adjudication(Base):
    def setUp(self):
        super().setUp()
        self.items, _ = tools.load_items(self.write("c.json", placeholder_corpus()))

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

    def test_agreement_flags_disagreement_and_cannot_decide_for_the_tiebreaker(self):
        ids = [i["id"] for i in self.items if i["lang"] == "en"][:4]
        votes = {ids[0]: ("reassures", "reassures"), ids[1]: ("reassures", "does_not_reassure"),
                 ids[2]: ("cannot_decide", "cannot_decide"), ids[3]: ("does_not_reassure", "does_not_reassure")}
        records = [{"adjudicator": who, "item": item, "verdict": v[n]}
                   for item, v in votes.items() for n, who in enumerate(("ana", "bruno"))]
        report = tools.agreement(self.items, records, ("ana", "bruno"))
        self.assertEqual(report["needs_tiebreak"], sorted([ids[1], ids[2]]))
        self.assertEqual(report["by_language"]["en"]["items_judged_by_both"], 4)
        self.assertEqual(report["by_language"]["en"]["percent_agreement"], 75.0)

    def test_final_label_rule(self):
        pair = ("ana", "bruno", "carla")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "reassures"}, *pair), "reassures")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "does_not_reassure", "carla": "does_not_reassure"}, *pair), "does_not_reassure")
        self.assertEqual(tools.final_label({"ana": "reassures", "bruno": "does_not_reassure"}, *pair), "unresolved")
        self.assertEqual(tools.final_label({"ana": "cannot_decide", "bruno": "cannot_decide", "carla": "cannot_decide"}, *pair), "unresolved")


if __name__ == "__main__":
    unittest.main()
