import unittest
from unittest.mock import patch

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.observation import Observation
from webapp.digital_twin.twin_intelligence import TwinIntelligence


class TwinIntelligenceTests(unittest.TestCase):
    def test_twin_intelligence_merges_ai_outputs(self) -> None:
        intelligence = TwinIntelligence()
        observation = Observation(
            cow_id="cow-001",
            age=36.0,
            weight=550.0,
            feed=25.0,
            temperature=31.0,
            humidity=68.0,
            health_status=1,
            notes="test observation",
        )

        result = intelligence.analyze_observation(observation)

        self.assertIsNotNone(result.prediction)
        self.assertIsNotNone(result.health)
        self.assertIsNotNone(result.explanation)
        self.assertIn("prediction", result.prediction)
        self.assertIn("severity", result.health)
        self.assertTrue(result.explanation)

    def test_weather_failure_returns_none_weather(self) -> None:
        intelligence = TwinIntelligence()
        observation = Observation(cow_id="cow-002", age=24.0, weight=500.0, feed=20.0, temperature=29.0, humidity=62.0)

        with patch("webapp.digital_twin.twin_intelligence.get_current_weather", side_effect=RuntimeError("weather unavailable")):
            result = intelligence.analyze_observation(observation)

        self.assertIsNone(result.weather)
        self.assertIn("service_errors", result.metadata)

    def test_missing_observation_leaves_cow_twin_unmodified(self) -> None:
        cow = CowTwin(cow_id="cow-003")

        cow.refresh_from_ai()

        self.assertIsNone(cow.latest_intelligence)
        self.assertEqual(cow.state.status, "stable")

    def test_adapter_injection_is_used_for_weather_and_simulation(self) -> None:
        def weather_adapter(observation: Observation) -> dict[str, float]:
            return {"temperature": 22.0, "humidity": 58.0}

        def simulation_adapter(observation: Observation, result: object) -> dict[str, str]:
            return {"mode": "custom", "cow_id": observation.cow_id}

        intelligence = TwinIntelligence(weather_adapter=weather_adapter, simulation_adapter=simulation_adapter)
        observation = Observation(cow_id="cow-004", age=30.0, weight=540.0, feed=22.0, temperature=30.0, humidity=64.0)

        result = intelligence.analyze_observation(observation)

        self.assertEqual(result.weather, {"temperature": 22.0, "humidity": 58.0})
        self.assertEqual(result.simulation, {"mode": "custom", "cow_id": observation.cow_id})


if __name__ == "__main__":
    unittest.main()
