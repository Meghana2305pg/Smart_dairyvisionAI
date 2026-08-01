import unittest

from webapp.screens.command_centre import build_command_centre_context


class CommandCentreWorkspaceTests(unittest.TestCase):
    def test_build_command_centre_context_assembles_dashboard_payload(self) -> None:
        payload = build_command_centre_context(
            cows=[{"cow_id": "cow-001", "name": "Mabel", "breed": "Holstein", "health_status": 0}],
            observations=[{"cow_id": "cow-001", "notes": "Routine check"}],
            predictions=[{"cow_id": "cow-001", "prediction": 24.9}],
            health=[{"cow_id": "cow-001", "severity": "Low", "alert_category": "Healthy"}],
            recommendations=[{"cow_id": "cow-001", "message": "Maintain monitoring", "priority": "Low"}],
            twin_states=[{"cow_id": "cow-001", "status": "stable", "last_updated": "2026-01-01T08:00:00"}],
            weather=(31.0, 68.0),
        )

        self.assertEqual(payload["summary"]["total_cows"], 1)
        self.assertEqual(payload["summary"]["healthy_cows"], 1)
        self.assertEqual(payload["summary"]["active_predictions"], 1)
        self.assertEqual(payload["twin_monitor"][0]["cow_id"], "cow-001")
        self.assertEqual(payload["alerts"]["critical"], [])
        self.assertEqual(payload["weather"]["temperature"], 31.0)
        self.assertEqual(payload["recommendations"]["health"][0]["cow_id"], "cow-001")


if __name__ == "__main__":
    unittest.main()
