import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from webapp.repositories.cow_repository import CowRepository
from webapp.repositories.supabase_client import SupabaseClient
from webapp.services.auth_service import AuthService
from webapp.services.cow_service import CowService
from webapp.services.dashboard_service import DashboardService
from webapp.services.farm_service import FarmService
from webapp.services.observation_service import ObservationService
from webapp.digital_twin.cow_twin import CowTwin


class ApplicationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supabase_available_patcher = patch.object(SupabaseClient, "_remote_available", return_value=False)
        self.supabase_available_patcher.start()
        SupabaseClient.from_env().reset_in_memory_store()

    def tearDown(self) -> None:
        SupabaseClient.from_env().reset_in_memory_store()
        self.supabase_available_patcher.stop()

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
        self.assertEqual(result["cow_twin"]["cow_id"], "cow-202")

    def test_observation_service_uses_cow_uuid_when_cow_tag_is_selected(self) -> None:
        from uuid import uuid4

        client = SupabaseClient.from_env()
        client.reset_in_memory_store()
        client._client = None
        cow_uuid = str(uuid4())
        client.get_table("cows").append({"id": cow_uuid, "cow_tag": "cow-001", "cow_name": "Bella"})

        cow_service = CowService()
        observation_service = ObservationService(cow_service=cow_service)

        saved_payload: dict[str, object] = {}
        original_create = observation_service.repository.create

        def capture(payload: dict[str, object]) -> dict[str, object]:
            saved_payload.update(payload)
            return payload

        observation_service.repository.create = capture
        observation_service.record_observation(
            cow_id="cow-001",
            age=24.0,
            weight=500.0,
            feed=20.0,
            temperature=30.0,
            humidity=70.0,
            health_status=0,
            notes="test note",
        )
        observation_service.repository.create = original_create

        self.assertEqual(saved_payload["cow_id"], cow_uuid)
        self.assertEqual(saved_payload["feed"], 20.0)
        self.assertEqual(saved_payload["temperature"], 30.0)
        self.assertEqual(saved_payload["humidity"], 70.0)
        self.assertEqual(saved_payload["health_status"], 0)
        self.assertEqual(saved_payload["notes"], "test note")

    def test_remote_cow_repository_get_uses_cow_tag_for_non_uuid_values(self) -> None:
        from uuid import uuid4

        with patch.object(SupabaseClient, "_remote_available", return_value=True):
            client = SupabaseClient.from_env()
            calls: list[dict[str, str]] = []

            def fake_list_by(table_name: str, filters: dict[str, str]) -> list[dict[str, str]]:
                calls.append(filters)
                if filters == {"cow_tag": "cow-001"}:
                    return [{"id": "uuid-test-123", "cow_tag": "cow-001", "cow_name": "Bella"}]
                return []

            client.list_by = fake_list_by  # type: ignore[assignment]
            repo = CowRepository(client=client)

            cow_record = repo.get("cow-001")

        self.assertEqual(cow_record["id"], "uuid-test-123")
        self.assertEqual(calls[0], {"cow_tag": "cow-001"})

    def test_observation_service_resolves_cow_id_uuid_from_local_cow_record(self) -> None:
        from uuid import uuid4

        client = SupabaseClient.from_env()
        client.reset_in_memory_store()
        client._client = None
        cow_uuid = str(uuid4())
        client.get_table("cows").append({"id": cow_uuid, "cow_tag": "cow-001", "cow_name": "Bella"})

        cow_service = CowService()
        observation_service = ObservationService(cow_service=cow_service)

        saved_payload: dict[str, object] = {}
        original_create = observation_service.repository.create

        def capture(payload: dict[str, object]) -> dict[str, object]:
            saved_payload.update(payload)
            return payload

        observation_service.repository.create = capture
        observation_service.record_observation(
            cow_id=cow_uuid,
            age=24.0,
            weight=500.0,
            feed=20.0,
            temperature=30.0,
            humidity=70.0,
            health_status=0,
            notes="uuid selection test",
        )
        observation_service.repository.create = original_create

        self.assertEqual(saved_payload["cow_id"], cow_uuid)
        self.assertEqual(saved_payload["notes"], "uuid selection test")

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

    def test_dashboard_service_uses_cow_service_repository_for_cow_count(self) -> None:
        class EmptyDashboardRepository:
            def get_farms(self) -> list[dict[str, object]]:
                return []

            def get_cows(self) -> list[dict[str, object]]:
                return []

            def get_observations(self) -> list[dict[str, object]]:
                return []

            def get_snapshots(self) -> list[dict[str, object]]:
                return []

        cow_service = CowService()
        cow_service.repository.list = lambda: [{"cow_tag": "cow-777", "cow_name": "Mina"}]
        dashboard_service = DashboardService(repository=EmptyDashboardRepository(), cow_service=cow_service)

        dashboard = dashboard_service.build_dashboard()

        self.assertEqual(dashboard.herd["cow_count"], 1)

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
