import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from webapp.repositories.supabase_client import SupabaseClient
from webapp.services.auth_service import AuthService
from webapp.services.cow_service import CowService
from webapp.services.dashboard_service import DashboardService
from webapp.services.farm_service import FarmService
from webapp.services.observation_service import ObservationService


class ApplicationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        SupabaseClient.from_env().reset_in_memory_store()

    def tearDown(self) -> None:
        SupabaseClient.from_env().reset_in_memory_store()

    def test_supabase_client_creates_from_environment(self) -> None:
        with patch.dict(os.environ, {"SUPABASE_URL": "https://demo.supabase.co", "SUPABASE_ANON_KEY": "demo-key"}, clear=False):
            client = SupabaseClient.from_env()

        self.assertEqual(client.url, "https://demo.supabase.co")
        self.assertEqual(client.key, "demo-key")

    def test_farm_service_creates_farm_and_initializes_twin(self) -> None:
        service = FarmService()

        result = service.create_farm(farm_id="farm-001", name="North Farm", location="Nairobi")

        self.assertEqual(result["farm"]["farm_id"], "farm-001")
        self.assertIn("farm-001", service._farm_twins)

    def test_cow_service_registers_cow_and_creates_twin(self) -> None:
        service = CowService()

        result = service.register_cow(cow_id="cow-101", name="Molly", breed="Holstein", age_months=30)

        self.assertEqual(result["cow"]["cow_id"], "cow-101")
        self.assertEqual(result["cow"]["breed"], "Holstein")
        self.assertEqual(result["cow"]["age_months"], 30)
        self.assertIn("cow-101", service._cow_twins)

    def test_observation_service_records_observation_into_twin_and_snapshot(self) -> None:
        cow_service = CowService()
        observation_service = ObservationService(cow_service=cow_service)
        cow_service.register_cow(cow_id="cow-202", name="Daisy")

        result = observation_service.record_observation(
            cow_id="cow-202",
            age=36.0,
            weight=560.0,
            feed=24.0,
            temperature=31.0,
            humidity=68.0,
            health_status=1,
            notes="hot day",
        )

        self.assertEqual(result["snapshot"].cow_id, "cow-202")
        self.assertIn("latest_snapshot_id", result["cow_twin"]["state"]["context"])

    def test_dashboard_service_aggregates_farm_herd_predictions_health_and_snapshots(self) -> None:
        farm_service = FarmService()
        cow_service = CowService()
        observation_service = ObservationService(cow_service=cow_service)
        dashboard_service = DashboardService(farm_service=farm_service, cow_service=cow_service, observation_service=observation_service)

        farm_service.create_farm(farm_id="farm-900", name="West Farm", location="Kisumu")
        cow_service.register_cow(cow_id="cow-900", name="Nia")
        observation_service.record_observation(
            cow_id="cow-900",
            age=30.0,
            weight=520.0,
            feed=22.0,
            temperature=30.0,
            humidity=65.0,
            health_status=1,
            notes="stable",
        )

        dashboard = dashboard_service.build_dashboard()

        self.assertEqual(dashboard.farm["farm_id"], "farm-900")
        self.assertEqual(dashboard.herd["cow_count"], 1)
        self.assertTrue(dashboard.predictions)
        self.assertTrue(dashboard.snapshots)

    def test_auth_service_registers_and_tracks_current_user(self) -> None:
        class FakeAuth:
            def sign_up(self, payload: dict[str, str]) -> SimpleNamespace:
                return SimpleNamespace(user=SimpleNamespace(id="user-1", email=payload["email"]), session=None)

            def sign_in_with_password(self, payload: dict[str, str]) -> SimpleNamespace:
                return SimpleNamespace(user=SimpleNamespace(id="user-1", email=payload["email"]), session=SimpleNamespace(model_dump=lambda: {"access_token": "abc"}))

            def sign_out(self) -> None:
                return None

        with patch("webapp.repositories.supabase_client.create_client", return_value=SimpleNamespace(auth=FakeAuth())):
            service = AuthService(client=SupabaseClient(url="https://demo.supabase.co", key="demo-key"))

            user = service.register_user(email="farmer@example.com", password="secret123")
            logged_in = service.login(email="farmer@example.com", password="secret123")

            self.assertEqual(user["email"], "farmer@example.com")
            self.assertTrue(logged_in)
            self.assertEqual(service.current_user()["email"], "farmer@example.com")

            service.logout()
            self.assertIsNone(service.current_user())


if __name__ == "__main__":
    unittest.main()
