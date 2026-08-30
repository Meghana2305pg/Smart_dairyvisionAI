import unittest
from datetime import datetime

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

    def test_build_analytics_context_resolves_uuid_observations_to_predicted_cow_tags(self) -> None:
        payload = build_analytics_context(
            cow_records=[
                {"id": "11111111-1111-4111-8111-111111111111", "cow_id": "cow-001", "cow_tag": "cow-001", "name": "Mabel", "breed": "Holstein", "health_status": 0},
                {"id": "22222222-2222-4222-8222-222222222222", "cow_id": "cow-002", "cow_tag": "cow-002", "name": "Bess", "breed": "Jersey", "health_status": 1},
            ],
            observations=[
                {
                    "cow_id": "11111111-1111-4111-8111-111111111111",
                    "timestamp": datetime(2026, 1, 1, 8, 0, 0),
                    "temperature": 27.0,
                    "humidity": 61.0,
                    "feed": 24.0,
                    "weight": 520.0,
                    "health_status": 0,
                },
                {
                    "cow_id": "22222222-2222-4222-8222-222222222222",
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

        self.assertEqual(payload["summary"]["average_milk_yield"], 22.3)
        self.assertEqual(payload["chart_observations"][0]["yield"], 28.4)
        self.assertEqual(payload["top_performing"][0]["predicted_yield"], 28.4)
        self.assertEqual(payload["top_performing"][0]["cow_id"], "cow-001")


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
