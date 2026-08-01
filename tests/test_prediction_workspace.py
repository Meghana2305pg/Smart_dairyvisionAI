import unittest

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.observation import Observation
from webapp.screens.prediction import build_prediction_context


class PredictionWorkspaceTests(unittest.TestCase):
    def test_build_prediction_context_assembles_prediction_workspace(self) -> None:
        twin = CowTwin(cow_id="cow-001", name="Mabel")
        observation = Observation(
            cow_id="cow-001",
            age=28.0,
            weight=520.0,
            feed=24.0,
            temperature=31.0,
            humidity=68.0,
            health_status=0,
            notes="Routine midday check",
        )
        twin.record_observation(observation)
        twin.refresh_from_ai(base_temp=31.0, base_hum=68.0)

        payload = build_prediction_context(
            cow_twin=twin,
            cow_record={"cow_id": "cow-001", "name": "Mabel", "breed": "Holstein", "age_months": 28},
            observations=[{"cow_id": "cow-001", "notes": "Routine midday check", "timestamp": observation.timestamp, "temperature": 31.0, "humidity": 68.0, "feed": 24.0, "weight": 520.0, "health_status": 0}],
            weather=(31.0, 68.0),
            prediction={"prediction": 24.9, "feature_names": ["feed", "temperature"], "feature_values": {"feed": 24.0, "temperature": 31.0}},
            health={"alert_category": "Healthy", "severity": "Low", "recommendation": "Continue monitoring"},
            explanation=[{"feature": "feed", "contribution": 0.35}],
            history=[{"step": 1, "value": 22.4}, {"step": 2, "value": 24.9}],
            recommendations=[{"message": "Continue monitoring", "priority": "Low"}],
            model_version="1.0.0",
        )

        self.assertEqual(payload["cow_id"], "cow-001")
        self.assertEqual(payload["prediction"], 24.9)
        self.assertEqual(payload["weather"]["temperature"], 31.0)
        self.assertEqual(payload["health_status"]["alert_category"], "Healthy")
        self.assertEqual(payload["model_inputs"]["feed"], 24.0)
        self.assertEqual(payload["feature_importance"][0]["feature"], "feed")
        self.assertEqual(payload["history"][0]["value"], 22.4)
        self.assertEqual(payload["recommendations"][0]["message"], "Continue monitoring")
        self.assertEqual(payload["model_version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
