import ast
import unittest
from datetime import datetime
from pathlib import Path

from webapp.digital_twin.decision_support import Recommendation
from webapp.screens.analytics import build_analytics_context


class AnalyticsWorkspaceTests(unittest.TestCase):
    def test_build_analytics_context_assembles_kpis_and_rankings(self) -> None:
        payload = build_analytics_context(
            cow_records=[
                {"cow_id": "cow-001", "name": "Mabel", "breed": "Holstein", "health_status": 0},
                {"cow_id": "cow-002", "name": "Bess", "breed": "Jersey", "health_status": 1},
            ],
            observations=[
                {
                    "cow_id": "cow-001",
                    "timestamp": datetime(2026, 1, 1, 8, 0, 0),
                    "temperature": 27.0,
                    "humidity": 61.0,
                    "feed": 24.0,
                    "weight": 520.0,
                    "health_status": 0,
                },
                {
                    "cow_id": "cow-002",
                    "timestamp": datetime(2026, 1, 2, 8, 0, 0),
                    "temperature": 35.0,
                    "humidity": 72.0,
                    "feed": 18.0,
                    "weight": 480.0,
                    "health_status": 1,
                },
            ],
            predictions=[{"cow_id": "cow-001", "prediction": 28.4}, {"cow_id": "cow-002", "prediction": 16.2}],
            health=[{"cow_id": "cow-001", "severity": "Low"}, {"cow_id": "cow-002", "severity": "High"}],
            recommendations=[{"cow_id": "cow-001", "message": "Maintain monitoring"}],
            weather=(30.0, 64.0),
        )

        self.assertEqual(payload["summary"]["total_cows"], 2)
        self.assertEqual(payload["summary"]["healthy_cows"], 1)
        self.assertEqual(payload["summary"]["sick_cows"], 1)
        self.assertEqual(payload["summary"]["average_milk_yield"], 22.3)
        self.assertEqual(payload["summary"]["active_alerts"], 1)
        self.assertEqual(payload["top_performing"][0]["cow_id"], "cow-001")
        self.assertEqual(payload["poor_performing"][0]["cow_id"], "cow-002")
        self.assertEqual(payload["insights"][0]["title"], "AI Insight")

    def test_build_analytics_context_accepts_recommendation_objects(self) -> None:
        payload = build_analytics_context(
            recommendations=[Recommendation("Escalate review", "high")],
            weather=(25.0, 60.0),
        )

        self.assertIn("Escalate review", payload["insights"][0]["description"])

    def test_plotly_charts_define_explicit_keys(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        target_files = [
            repo_root / "webapp/screens/analytics.py",
            repo_root / "webapp/ui/analytics_views.py",
            repo_root / "webapp/pages/01_Prediction.py",
            repo_root / "webapp/pages/02_Digital_Twin.py",
            repo_root / "webapp/pages/04_Explainability.py",
            repo_root / "webapp/screens/explainability.py",
        ]

        for file_path in target_files:
            tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Attribute) or node.func.attr != "plotly_chart":
                    continue
                if not any(isinstance(keyword, ast.keyword) and keyword.arg == "key" for keyword in node.keywords):
                    self.fail(f"{file_path.relative_to(repo_root)} is missing a key argument for st.plotly_chart")


if __name__ == "__main__":
    unittest.main()
