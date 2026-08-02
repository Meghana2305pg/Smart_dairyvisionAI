import unittest

from webapp.digital_twin.scenario_engine import Scenario
from webapp.screens.scenario_studio import _build_changed_features, _build_scenario_summary


class ScenarioStudioTests(unittest.TestCase):
    def test_build_changed_features_returns_only_changed_inputs(self) -> None:
        live_context = {
            "observation": {"feed": 18.0, "weight": 500.0},
            "weather": {"temperature": 28.0, "humidity": 65.0},
            "thi": 28.2,
        }
        scenario = Scenario(
            scenario_id="scenario-1",
            cow_id="cow-001",
            created_at=None,  # type: ignore[arg-type]
            name="Test",
            description="Test",
            base_snapshot_id="snapshot-1",
            modified_inputs={"feed_intake": 22.0, "temperature": 31.0},
            weather={"temperature": 31.0, "humidity": 65.0},
        )

        changed_features = _build_changed_features(live_context, scenario)

        self.assertEqual(changed_features, ["Feed Intake", "Temperature"])

    def test_build_scenario_summary_uses_comparison_data(self) -> None:
        live_context = {
            "observation": {"feed": 18.0},
            "weather": {"temperature": 28.0, "humidity": 65.0},
            "thi": 28.2,
        }
        scenario = Scenario(
            scenario_id="scenario-1",
            cow_id="cow-001",
            created_at=None,  # type: ignore[arg-type]
            name="Test",
            description="Test",
            base_snapshot_id="snapshot-1",
            modified_inputs={"feed_intake": 22.0},
            prediction={"prediction": 30.1},
            health_assessment={"severity": "Healthy"},
            weather={"temperature": 29.0, "humidity": 65.0},
        )

        summary = _build_scenario_summary(live_context, scenario, 2.1)

        self.assertIn("Increasing feed intake", summary)
        self.assertIn("30.1", summary)
        self.assertIn("Healthy", summary)


if __name__ == "__main__":
    unittest.main()
