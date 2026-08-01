import unittest
from datetime import datetime

from webapp.screens.explainability import build_explainability_context


class ExplainabilityWorkspaceTests(unittest.TestCase):
    def test_build_explainability_context_assembles_workspace_payload(self) -> None:
        payload = build_explainability_context(
            cow_record={"cow_id": "cow-001", "name": "Mabel", "breed": "Holstein"},
            observations=[
                {"cow_id": "cow-001", "timestamp": datetime(2026, 1, 1, 8, 0, 0), "notes": "Routine check", "temperature": 31.0, "humidity": 68.0, "feed": 24.0, "weight": 520.0, "health_status": 0},
            ],
            prediction={"prediction": 24.9},
            explanation=[{"feature": "feed", "contribution": 0.35}, {"feature": "temperature", "contribution": -0.15}],
            weather=(31.0, 68.0),
            model_version="1.0.0",
            risk_level="Low",
        )

        self.assertEqual(payload["summary"]["predicted_milk_yield"], 24.9)
        self.assertEqual(payload["summary"]["model_version"], "1.0.0")
        self.assertEqual(payload["summary"]["risk_level"], "Low")
        self.assertEqual(payload["feature_table"][0]["feature"], "feed")
        self.assertEqual(payload["explanations"][0]["title"], "Feature Driver")
        self.assertEqual(payload["comparison"]["current_prediction"], 24.9)


if __name__ == "__main__":
    unittest.main()
