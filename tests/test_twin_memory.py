import unittest
from datetime import datetime

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.farm_twin import FarmTwin
from webapp.digital_twin.herd_twin import HerdTwin
from webapp.digital_twin.memory.memory_store import InMemorySnapshotStore
from webapp.digital_twin.memory.snapshot import TwinSnapshot
from webapp.digital_twin.observation import Observation


class TwinMemoryTests(unittest.TestCase):
    def test_save_and_load_snapshot(self) -> None:
        store = InMemorySnapshotStore()
        snapshot = TwinSnapshot(
            snapshot_id="snap-1",
            cow_id="cow-001",
            timestamp=datetime.utcnow(),
            observation=Observation(cow_id="cow-001", age=24.0, weight=490.0),
            prediction={"prediction": 18.5},
            health={"severity": "Low"},
            weather={"temperature": 24.0, "humidity": 60.0},
            explanation=[{"feature": "feed", "contribution": 0.2}],
            recommendations=[{"message": "keep monitoring", "priority": "low"}],
            twin_status="stable",
            metadata={"source": "test"},
        )

        store.save_snapshot(snapshot)
        loaded = store.load_snapshot("snap-1")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.snapshot_id, "snap-1")

    def test_latest_snapshot_and_ordering(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-a", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-b", cow_id="cow-001", timestamp=datetime(2024, 1, 2), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        history = store.list_snapshot_history("cow-001")
        latest = store.get_latest_snapshot("cow-001")

        self.assertEqual([item.snapshot_id for item in history], ["snap-a", "snap-b"])
        self.assertEqual(latest.snapshot_id, "snap-b")

    def test_missing_snapshot_returns_none(self) -> None:
        store = InMemorySnapshotStore()
        self.assertIsNone(store.load_snapshot("missing"))
        self.assertIsNone(store.get_latest_snapshot("cow-999"))

    def test_multiple_cows_and_memory_isolation(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-c", cow_id="cow-001", timestamp=datetime.utcnow(), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-d", cow_id="cow-002", timestamp=datetime.utcnow(), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        self.assertEqual(len(store.list_snapshot_history("cow-001")), 1)
        self.assertEqual(len(store.list_snapshot_history("cow-002")), 1)
        self.assertEqual(store.get_latest_snapshot("cow-001").snapshot_id, "snap-c")
        self.assertEqual(store.get_latest_snapshot("cow-002").snapshot_id, "snap-d")

    def test_cow_twin_records_snapshot_in_memory_store(self) -> None:
        cow = CowTwin(cow_id="cow-777")
        cow.record_observation(Observation(cow_id="cow-777", age=30.0, weight=520.0, feed=22.0, temperature=30.0, humidity=65.0, health_status=1))
        cow.refresh_from_ai()

        snapshot = cow.memory_store.get_latest_snapshot("cow-777")
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.cow_id, "cow-777")
        self.assertEqual(cow.state.context["latest_snapshot_id"], snapshot.snapshot_id)

    def test_herd_and_farm_aggregate_latest_snapshots(self) -> None:
        cow_one = CowTwin(cow_id="cow-1")
        cow_two = CowTwin(cow_id="cow-2")
        cow_one.record_observation(Observation(cow_id="cow-1", age=30.0, weight=520.0, feed=22.0, temperature=30.0, humidity=65.0, health_status=1))
        cow_two.record_observation(Observation(cow_id="cow-2", age=32.0, weight=540.0, feed=24.0, temperature=31.0, humidity=70.0, health_status=1))
        cow_one.refresh_from_ai()
        cow_two.refresh_from_ai()

        herd = HerdTwin(herd_id="herd-1")
        herd.register_cow(cow_one)
        herd.register_cow(cow_two)
        summary = herd.aggregate_snapshot_summary()

        self.assertIn("average_prediction", summary)
        self.assertIn("average_health", summary)
        self.assertIn("average_thi", summary)
        self.assertIn("risk_summary", summary)

        farm = FarmTwin(farm_id="farm-1")
        farm.register_herd(herd)
        farm_summary = farm.aggregate_herd_summaries()
        self.assertIn("herd_count", farm_summary)


if __name__ == "__main__":
    unittest.main()
