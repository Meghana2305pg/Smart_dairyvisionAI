import unittest
from datetime import datetime

from webapp.digital_twin.cow_twin import CowTwin
from webapp.digital_twin.memory.memory_store import InMemorySnapshotStore
from webapp.digital_twin.memory.snapshot import TwinSnapshot
from webapp.digital_twin.observation import Observation
from webapp.digital_twin.scenario_engine import ScenarioEngine


class ScenarioEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemorySnapshotStore()
        self.base_snapshot = TwinSnapshot(
            snapshot_id="snap-live",
            cow_id="cow-001",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            observation=Observation(cow_id="cow-001", age=24.0, weight=490.0, feed=22.0, temperature=28.0, humidity=65.0, health_status=1),
            prediction={"prediction": 18.5},
            health={"severity": "Low"},
            weather={"temperature": 28.0, "humidity": 65.0},
            explanation=[{"feature": "feed", "contribution": 0.2}],
            recommendations=[{"message": "monitor", "priority": "low"}],
            twin_status="stable",
            metadata={"source": "test"},
        )
        self.store.save_snapshot(self.base_snapshot)

    def test_clone_snapshot_creates_isolated_copy(self) -> None:
        engine = ScenarioEngine(self.store)
        scenario = engine.create_scenario(
            cow_id="cow-001",
            base_snapshot_id="snap-live",
            name="Heat stress scenario",
            description="Simulate heat stress",
            modified_inputs={"temperature": 35.0, "humidity": 80.0},
        )

        self.assertEqual(scenario.base_snapshot_id, "snap-live")
        self.assertEqual(scenario.cow_id, "cow-001")
        self.assertEqual(scenario.modified_inputs["temperature"], 35.0)
        self.assertIsNotNone(scenario.prediction)
        self.assertEqual(len(engine.list_scenarios()), 1)

    def test_apply_changes_and_compare_live(self) -> None:
        engine = ScenarioEngine(self.store)
        scenario = engine.create_scenario(
            cow_id="cow-001",
            base_snapshot_id="snap-live",
            name="Feed change",
            description="Simulate lower feed intake",
            modified_inputs={"feed_intake": 15.0, "body_weight": 470.0},
        )
        comparison = engine.compare_with_live(scenario, self.base_snapshot)

        self.assertEqual(comparison.current_prediction["prediction"], self.base_snapshot.prediction["prediction"])
        self.assertEqual(comparison.scenario_prediction["prediction"], scenario.prediction["prediction"])
        self.assertIn("feed_intake", comparison.changed_features)
        self.assertIn("body_weight", comparison.changed_features)

    def test_multiple_scenarios_and_delete(self) -> None:
        engine = ScenarioEngine(self.store)
        first = engine.create_scenario("cow-001", "snap-live", "One", "First", {"temperature": 31.0})
        second = engine.create_scenario("cow-001", "snap-live", "Two", "Second", {"humidity": 90.0})

        self.assertEqual(len(engine.list_scenarios()), 2)
        engine.delete_scenario(first.scenario_id)
        self.assertEqual(len(engine.list_scenarios()), 1)
        self.assertEqual(engine.list_scenarios()[0].scenario_id, second.scenario_id)

    def test_live_twin_unchanged(self) -> None:
        engine = ScenarioEngine(self.store)
        cow = CowTwin(cow_id="cow-001")
        initial_context = dict(cow.state.context)

        engine.create_scenario(
            cow_id="cow-001",
            base_snapshot_id="snap-live",
            name="Live guard",
            description="Should not touch live twin",
            modified_inputs={"temperature": 34.0},
        )

        self.assertEqual(cow.state.context, initial_context)
        self.assertEqual(cow.state.status, "stable")


if __name__ == "__main__":
    unittest.main()
