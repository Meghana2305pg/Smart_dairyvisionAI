import unittest
from datetime import datetime

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.farm_twin import FarmTwin
from webapp.digital_twin.herd_twin import HerdTwin
from webapp.digital_twin.memory.memory_store import InMemorySnapshotStore
from webapp.digital_twin.memory.playback import PlaybackEngine
from webapp.digital_twin.memory.snapshot import TwinSnapshot
from webapp.digital_twin.memory.snapshot_engine import SnapshotEngine
from webapp.digital_twin.memory.timeline import TimelineEngine
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

    def test_snapshot_engine_creates_richer_snapshot(self) -> None:
        engine = SnapshotEngine()
        snapshot = engine.create_snapshot(
            cow_id="cow-100",
            observation=Observation(cow_id="cow-100", age=26.0, weight=500.0),
            prediction={"prediction": 18.0},
            health_assessment={"severity": "Low"},
            explainability=[{"feature": "feed", "contribution": 0.2}],
            recommendations=[{"message": "monitor", "priority": "low"}],
            twin_status="stable",
            weather={"temperature": 24.0, "humidity": 60.0},
            metadata={"source": "engine"},
        )

        self.assertEqual(snapshot.cow_id, "cow-100")
        self.assertEqual(snapshot.health_assessment["severity"], "Low")
        self.assertEqual(snapshot.explainability[0]["feature"], "feed")
        self.assertEqual(snapshot.version, 1)
        self.assertIsNotNone(snapshot.snapshot_id)
        self.assertIsNotNone(snapshot.timestamp)

    def test_snapshot_store_adds_extended_accessors(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-e", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-f", cow_id="cow-001", timestamp=datetime(2024, 1, 2), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        self.assertEqual(store.count(), 2)
        self.assertEqual(store.get_latest("cow-001").snapshot_id, "snap-f")
        self.assertEqual(store.get_snapshot("snap-e").snapshot_id, "snap-e")
        self.assertEqual([item.snapshot_id for item in store.get_history("cow-001")], ["snap-e", "snap-f"])
        self.assertEqual([item.snapshot_id for item in store.get_range("cow-001", datetime(2024, 1, 1), datetime(2024, 1, 2))], ["snap-e", "snap-f"])

    def test_timeline_engine_creates_and_orders_events(self) -> None:
        engine = TimelineEngine()
        first = engine.create_event(cow_id="cow-001", snapshot_id="snap-1", timestamp=datetime(2024, 1, 1), event_type="observation_recorded", title="Observation", summary="Recorded")
        second = engine.create_event(cow_id="cow-001", snapshot_id="snap-2", timestamp=datetime(2024, 1, 2), event_type="prediction_updated", title="Prediction", summary="Updated")
        engine.append_event(first)
        engine.append_event(second)

        history = engine.get_history("cow-001")
        latest = engine.get_latest_event("cow-001")
        filtered = engine.get_events_between("cow-001", datetime(2024, 1, 1), datetime(2024, 1, 2))

        self.assertEqual([item.event_type for item in history], ["observation_recorded", "prediction_updated"])
        self.assertEqual(latest.event_type, "prediction_updated")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(engine.count_events("cow-001"), 2)

    def test_timeline_engine_isolated_per_cow(self) -> None:
        engine = TimelineEngine()
        engine.append_event(engine.create_event(cow_id="cow-001", snapshot_id="snap-1", timestamp=datetime(2024, 1, 1), event_type="observation_recorded"))
        engine.append_event(engine.create_event(cow_id="cow-002", snapshot_id="snap-2", timestamp=datetime(2024, 1, 2), event_type="prediction_updated"))

        self.assertEqual(engine.count_events("cow-001"), 1)
        self.assertEqual(engine.count_events("cow-002"), 1)

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
        self.assertGreaterEqual(len(cow.state.timeline_events), 1)
        self.assertEqual(cow.timeline_engine.get_latest_event("cow-777").cow_id, "cow-777")

    def test_playback_first_and_last_snapshot(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-1", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-2", cow_id="cow-001", timestamp=datetime(2024, 1, 2), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        engine = PlaybackEngine(store, cow_id="cow-001")
        first_state = engine.first_snapshot()
        last_state = engine.last_snapshot()

        self.assertEqual(first_state.current_snapshot.snapshot_id, "snap-1")
        self.assertEqual(last_state.current_snapshot.snapshot_id, "snap-2")
        self.assertEqual(engine.current_snapshot().snapshot_id, "snap-2")

    def test_playback_previous_and_next_navigation(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-1", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-2", cow_id="cow-001", timestamp=datetime(2024, 1, 2), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        engine = PlaybackEngine(store, cow_id="cow-001")
        engine.first_snapshot()
        previous = engine.previous_snapshot()
        self.assertEqual(previous.current_snapshot.snapshot_id, "snap-1")

        engine.last_snapshot()
        next_state = engine.next_snapshot()
        self.assertEqual(next_state.current_snapshot.snapshot_id, "snap-2")

    def test_playback_boundaries_and_empty_history(self) -> None:
        store = InMemorySnapshotStore()
        engine = PlaybackEngine(store, cow_id="cow-001")

        self.assertIsNone(engine.current_snapshot())
        self.assertEqual(engine.total_snapshots(), 0)

        empty_state = engine.first_snapshot()
        self.assertIsNone(empty_state.current_snapshot)
        self.assertEqual(empty_state.playback_position, 0)

        first = TwinSnapshot(snapshot_id="snap-1", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        engine = PlaybackEngine(store, cow_id="cow-001")
        at_start = engine.first_snapshot()
        self.assertEqual(at_start.current_snapshot.snapshot_id, "snap-1")
        self.assertEqual(engine.previous_snapshot().current_snapshot.snapshot_id, "snap-1")
        self.assertEqual(engine.next_snapshot().current_snapshot.snapshot_id, "snap-1")

    def test_playback_isolated_per_cow(self) -> None:
        store = InMemorySnapshotStore()
        first = TwinSnapshot(snapshot_id="snap-1", cow_id="cow-001", timestamp=datetime(2024, 1, 1), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        second = TwinSnapshot(snapshot_id="snap-2", cow_id="cow-002", timestamp=datetime(2024, 1, 2), observation=None, prediction=None, health=None, weather=None, explanation=None, recommendations=None, twin_status="stable", metadata={})
        store.save_snapshot(first)
        store.save_snapshot(second)

        engine = PlaybackEngine(store, cow_id="cow-001")
        self.assertEqual(engine.total_snapshots(), 1)
        self.assertEqual(engine.current_snapshot().snapshot_id, "snap-1")

    def test_cow_twin_exposes_playback_engine(self) -> None:
        cow = CowTwin(cow_id="cow-888")
        playback = cow.get_playback()
        self.assertIsInstance(playback, PlaybackEngine)
        self.assertEqual(playback.cow_id, "cow-888")

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
