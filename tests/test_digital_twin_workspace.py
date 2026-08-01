import unittest

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.observation import Observation
from webapp.screens.digital_twin import build_dashboard_context


class DigitalTwinWorkspaceTests(unittest.TestCase):
    def test_build_dashboard_context_assembles_live_twin_state(self) -> None:
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

        payload = build_dashboard_context(
            cow_twin=twin,
            cow_record={"cow_id": "cow-001", "name": "Mabel", "breed": "Holstein", "age_months": 28},
            observations=[{"cow_id": "cow-001", "notes": "Routine midday check", "timestamp": observation.timestamp, "temperature": 31.0, "humidity": 68.0, "feed": 24.0, "weight": 520.0, "health_status": 0}],
            weather=(31.0, 68.0),
            prediction={"prediction": 24.9},
            health={"alert_category": "Healthy", "severity": "Low", "recommendation": "Continue monitoring"},
            explanation=[{"feature": "feed", "contribution": 0.3}],
            memory_snapshots=[{"snapshot_id": "snap-1", "timestamp": observation.timestamp, "twin_status": "stable"}],
        )

        self.assertEqual(payload["cow_id"], "cow-001")
        self.assertEqual(payload["latest_observation"]["notes"], "Routine midday check")
        self.assertEqual(payload["latest_prediction"]["prediction"], 24.9)
        self.assertEqual(payload["health_status"]["alert_category"], "Healthy")
        self.assertEqual(payload["weather"]["temperature"], 31.0)
        self.assertEqual(payload["thi"], 52.5)
        self.assertEqual(payload["recommendations"][0]["message"], "Continue monitoring")
        self.assertEqual(payload["timeline"][0]["notes"], "Routine midday check")
        self.assertEqual(payload["memory_info"]["snapshot_count"], 1)
        self.assertEqual(payload["explainability_summary"][0]["feature"], "feed")


if __name__ == "__main__":
    unittest.main()
