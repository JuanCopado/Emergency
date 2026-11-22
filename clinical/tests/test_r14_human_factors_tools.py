"""R14 · R5-1 policy layer 8 tooling (human factors). Uses only opaque codes and placeholder values."""
import ast
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import human_factors_tools as hf  # noqa: E402

TOOL = ROOT / "scripts" / "human_factors_tools.py"


def rec(participant="P01", task="T1", intended="ecg", chosen="ecg", outcome="correct", changes=0, seconds=12.5, role="physician"):
    return {"participant": participant, "role": role, "task_id": task, "intended_modality": intended,
            "chosen_modality": chosen, "changed_modality_count": changes, "outcome": outcome, "seconds": seconds}


class Validation(unittest.TestCase):
    def test_a_valid_set_passes(self):
        self.assertTrue(hf.validate_records([rec(), rec(task="T2", intended="xray", chosen="pocus", outcome="wrong_modality"),
                                             rec(task="T3", chosen=None, outcome="abandoned")]))

    def test_free_text_unknown_values_and_inconsistent_outcomes_are_rejected(self):
        for bad in (dict(rec(), comment="texto libre"), dict(rec(), name="Ana"), rec(participant="Ana Pérez"),
                    rec(role="student"), rec(intended="ct"), rec(chosen="ct"), rec(outcome="ok"),
                    rec(changes=-1), rec(changes=True), rec(changes=1.5), rec(seconds=-1), rec(seconds=float("inf")),
                    rec(chosen="xray", outcome="correct"), rec(chosen="ecg", outcome="wrong_modality"),
                    rec(chosen=None, outcome="wrong_modality"), rec(task="T 1")):
            with self.assertRaises(ValueError, msg=str(bad)):
                hf.validate_records([bad])
        with self.assertRaises(ValueError):
            hf.validate_records([])
        with self.assertRaises(ValueError):
            hf.validate_records([rec(), rec()])  # same participant and task twice


class Statistics(unittest.TestCase):
    def test_exact_interval_matches_known_values(self):
        low, high = hf.clopper_pearson(0, 10)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 1 - 0.025 ** (1 / 10), places=4)
        low, high = hf.clopper_pearson(10, 10)
        self.assertEqual(high, 1.0)
        self.assertAlmostEqual(low, 0.025 ** (1 / 10), places=4)
        low, high = hf.clopper_pearson(5, 10)
        self.assertAlmostEqual(low, 0.1871, places=3)
        self.assertAlmostEqual(high, 0.8129, places=3)

    def test_wilson_matches_known_values_and_empty_input_has_no_interval(self):
        low, high = hf.wilson(5, 10)
        self.assertAlmostEqual(low, 0.2366, places=3)
        self.assertAlmostEqual(high, 0.7634, places=3)
        self.assertIsNone(hf.wilson(0, 0))
        self.assertIsNone(hf.clopper_pearson(0, 0))
        self.assertIsNone(hf.clopper_pearson(3, 2))

    def test_extreme_sizes_and_the_precondition_of_the_binomial_mass(self):
        low, high = hf.clopper_pearson(0, 1)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.975, places=4)
        low, high = hf.clopper_pearson(500, 500)
        self.assertEqual(high, 1.0)
        self.assertAlmostEqual(low, 0.025 ** (1 / 500), places=4)
        low, high = hf.clopper_pearson(250, 500)
        self.assertAlmostEqual((low + high) / 2, 0.5, places=3)
        for p in (0, 1, -0.1, 1.5):
            with self.assertRaises(ValueError):
                hf._pmf(0, 5, p)

    def test_the_exact_interval_is_never_narrower_than_wilson_for_a_zero_count(self):
        self.assertGreaterEqual(hf.clopper_pearson(0, 30)[1], hf.wilson(0, 30)[1])


class Summary(unittest.TestCase):
    def test_summary_counts_rates_and_never_sets_a_threshold(self):
        records = [rec(participant=f"P{i:02d}", chosen="ecg") for i in range(8)]
        records += [rec(participant="P08", task="T2", intended="xray", chosen="pocus", outcome="wrong_modality", changes=1),
                    rec(participant="P09", task="T2", intended="xray", chosen=None, outcome="timeout")]
        out = hf.summarize(records)
        self.assertEqual(out["records"], 10)
        self.assertEqual(out["participants"], 10)
        self.assertEqual(out["residual_human_error"]["wrong_modality"], 1)
        self.assertAlmostEqual(out["residual_human_error"]["rate"], 0.1)
        self.assertEqual(out["by_intended_modality"]["xray"]["n"], 2)
        self.assertEqual(out["by_intended_modality"]["ecg"]["wrong_modality"], 0)
        self.assertEqual(out["changed_modality"]["sessions_with_a_change"], 1)
        self.assertEqual(out["outcomes"], {"correct": 8, "wrong_modality": 1, "timeout": 1})
        self.assertEqual(out["acceptance_threshold"], "NOT_SET_MEDICAL_DECISION")

    def test_cli_runs_over_standard_input_only(self):
        raw = json.dumps([rec()]).encode("utf-8")
        self.assertEqual(hf.run(["validate"], raw), {"valid": True, "records": 1})
        self.assertEqual(hf.run(["summarize"], raw)["records"], 1)


class Isolation(unittest.TestCase):
    def test_the_tool_has_no_file_system_or_network_access(self):
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertEqual(imported & {"os", "pathlib", "shutil", "tempfile", "glob", "io", "subprocess", "socket", "urllib"}, set())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertEqual(names & {"open", "Path", "eval", "exec", "__import__"}, set())
        self.assertEqual(attrs & {"read_text", "write_text", "read_bytes", "write_bytes", "mkdir", "unlink", "open"}, set())

    def test_nothing_in_the_product_uses_it(self):
        for path in list((ROOT / "scripts").glob("*.py")) + list((ROOT.parent / "app" / "src").rglob("*.ts*")):
            if path.name != "human_factors_tools.py":
                self.assertNotIn("human_factors_tools", path.read_text(encoding="utf-8", errors="ignore"), str(path))


if __name__ == "__main__":
    unittest.main()
