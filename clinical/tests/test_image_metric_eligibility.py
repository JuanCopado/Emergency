"""Synthetic evaluation tooling regression; no clinical images or outcomes."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from calculate_blinded_image_metrics import calculate


class ImageMetricEligibilityTests(unittest.TestCase):
    def test_nonblinded_data_cannot_calculate_metrics_without_request_flag(self):
        for dataset_class in ("teaching_source_known", "workflow_only"):
            for with_false_flag in (False, True):
                with self.subTest(dataset_class=dataset_class, false_flag=with_false_flag):
                    data = {
                        "dataset_class": dataset_class,
                        "cases": [
                            {"id": "synthetic-positive", "reference": {"target_positive": True},
                             "prediction": {"class": "positive"}},
                            {"id": "synthetic-negative", "reference": {"target_positive": False},
                             "prediction": {"class": "negative"}},
                        ],
                    }
                    if with_false_flag:
                        data["metrics_requested"] = False
                    result = calculate(data)
                    self.assertFalse(result["gate"]["metrics_eligible"])
                    self.assertIsNone(result["metrics"])
                    self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
