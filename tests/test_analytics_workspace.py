import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from webapp.screens.analytics import build_analytics_context, render_prediction_history
from webapp.screens.analytics_cards import render_summary_cards
from webapp.screens.charts import (
    build_health_trend_chart,
    build_milk_production_chart,
    build_prediction_history_chart,
    build_weather_vs_milk_chart,
)
from webapp.screens.filter_panel import render_filter_panel


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

    def test_end_date_includes_observations_later_that_day(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001", "name": "Mabel"}],
            observations=[{
                "cow_id": "cow-001",
                "created_at": "2026-08-31T10:30:00+00:00",
                "feed": 24.0,
                "temperature": 27.0,
                "humidity": 61.0,
                "health_status": 1,
            }],
            predictions=[{"cow_id": "cow-001", "prediction": 28.4}],
            date_range=("2026-08-31", "2026-08-31"),
        )

        self.assertEqual(len(payload["chart_observations"]), 1)

    @patch("webapp.screens.filter_panel.st")
    def test_default_date_range_includes_all_available_observations(self, streamlit_mock: MagicMock) -> None:
        streamlit_mock.container.return_value = MagicMock()
        streamlit_mock.columns.side_effect = ([MagicMock(), MagicMock()], [MagicMock(), MagicMock(), MagicMock()])
        streamlit_mock.checkbox.return_value = True
        streamlit_mock.selectbox.side_effect = ["All", "All", "All"]

        start_date, end_date, *_ = render_filter_panel(["cow-001"], ["Holstein"], ["healthy", "sick"])

        self.assertIsNone(start_date)
        self.assertIsNone(end_date)
        self.assertTrue(streamlit_mock.date_input.call_args_list[0].kwargs["disabled"])

    def test_observation_charts_receive_available_observations(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001"}],
            observations=[{
                "cow_id": "cow-001",
                "created_at": "2026-08-07T10:38:24+00:00",
                "temperature": 21.7,
                "humidity": 93.0,
                "health_status": 0,
            }],
            predictions=[{"cow_id": "cow-001", "prediction": 19.3}],
            date_range=(None, None),
        )

        self.assertEqual(len(payload["chart_observations"]), 1)
        self.assertEqual(len(build_milk_production_chart(payload["chart_observations"]).data), 1)
        self.assertEqual(len(build_health_trend_chart(payload["chart_observations"]).data), 1)
        self.assertEqual(len(build_weather_vs_milk_chart(payload["chart_observations"]).data), 1)

    def test_latest_persisted_observation_health_status_is_used(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001", "health_status": 0}],
            observations=[
                {"cow_id": "cow-001", "created_at": "2026-08-01T09:00:00Z", "health_status": 0},
                {"cow_id": "cow-001", "created_at": "2026-08-02T09:00:00Z", "health_status": 1},
            ],
            predictions=[{"cow_id": "cow-001", "prediction": 22.0}],
        )

        self.assertEqual(payload["top_performing"][0]["health_status"], 1)

    def test_missing_health_status_remains_unavailable(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001", "health_status": 0}],
            observations=[{"cow_id": "cow-001", "created_at": "2026-08-01T09:00:00Z"}],
            predictions=[{"cow_id": "cow-001", "prediction": 22.0}],
        )

        self.assertIsNone(payload["top_performing"][0]["health_status"])

    def test_feed_is_never_used_as_milk_yield(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001"}],
            observations=[{
                "cow_id": "cow-001",
                "created_at": "2026-08-01T09:00:00Z",
                "feed": 24.0,
                "temperature": 27.0,
                "humidity": 61.0,
                "health_status": 0,
            }],
            predictions=[],
        )

        self.assertIsNone(payload["chart_observations"][0]["yield"])
        self.assertEqual(len(build_milk_production_chart(payload["chart_observations"]).data), 0)
        self.assertEqual(len(build_weather_vs_milk_chart(payload["chart_observations"]).data), 0)

    def test_empty_predictions_do_not_create_history_points(self) -> None:
        payload = build_analytics_context(cow_records=[{"cow_id": "cow-001"}], predictions=[])

        self.assertEqual(payload["history"], [])
        self.assertEqual(len(build_prediction_history_chart(payload["history"]).data), 0)

    def test_current_recomputed_predictions_are_excluded_from_history(self) -> None:
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001"}],
            predictions=[{"cow_id": "cow-001", "prediction": 19.3, "source": "current_recomputed"}],
        )

        self.assertEqual(payload["history"], [])

    @patch("webapp.screens.analytics.st.info")
    @patch("webapp.screens.analytics.st.plotly_chart")
    def test_prediction_history_empty_state_is_shown(self, plotly_chart_mock: MagicMock, info_mock: MagicMock) -> None:
        render_prediction_history([])

        plotly_chart_mock.assert_not_called()
        info_mock.assert_called_once_with(
            "No prediction history available yet. Historical prediction points will appear after predictions are persisted."
        )

    @patch("webapp.screens.analytics_cards.st")
    def test_summary_cards_use_native_streamlit_metrics(self, streamlit_mock: MagicMock) -> None:
        streamlit_mock.columns.return_value = [MagicMock() for _ in range(6)]

        render_summary_cards({"total_cows": 2, "average_milk_yield": None, "today_prediction": None})

        self.assertEqual(streamlit_mock.metric.call_count, 6)
        values = [call.kwargs["value"] for call in streamlit_mock.metric.call_args_list]
        self.assertIn("Unavailable L", values)

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

    def test_build_analytics_context_handles_recommendation_objects(self) -> None:
        """Test that Recommendation dataclass objects are safely extracted."""
        from webapp.digital_twin.decision_support import Recommendation

        # Use Recommendation objects instead of dicts
        recommendation_obj = Recommendation(
            message="Escalate the cow review and inspect feed and heat stress exposure.",
            priority="high"
        )

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
            recommendations=[recommendation_obj],
            weather=(30.0, 64.0),
        )

        # Verify the recommendation message was correctly extracted
        self.assertEqual(payload["summary"]["total_cows"], 2)
        self.assertEqual(payload["insights"][0]["title"], "AI Insight")
        self.assertIn("Escalate the cow review", payload["insights"][0]["description"])

    def test_build_analytics_context_handles_empty_recommendation_message(self) -> None:
        """Test that fallback message is used when recommendation is empty/invalid."""
        payload = build_analytics_context(
            cow_records=[{"cow_id": "cow-001", "name": "Mabel"}],
            observations=[{
                "cow_id": "cow-001",
                "timestamp": datetime(2026, 1, 1, 8, 0, 0),
                "temperature": 27.0,
                "humidity": 61.0,
                "feed": 24.0,
                "weight": 520.0,
                "health_status": 0,
            }],
            predictions=[{"cow_id": "cow-001", "prediction": 28.4}],
            health=[{"cow_id": "cow-001", "severity": "Low"}],
            recommendations=[{}],  # Empty dict recommendation
            weather=(28.0, 64.0),
        )

        # Verify fallback message is used
        self.assertEqual(payload["insights"][0]["title"], "AI Insight")
        self.assertEqual(payload["insights"][0]["description"], "Review the latest observations to improve herd performance.")


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
