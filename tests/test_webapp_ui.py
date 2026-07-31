import unittest
from types import SimpleNamespace

from webapp.screens.dashboard import _get_latest_twin_snapshot


class DashboardSnapshotTests(unittest.TestCase):
    def test_get_latest_twin_snapshot_prefers_latest_submitted_cow_state(self) -> None:
        snapshot = SimpleNamespace(cow_id="cow-1")
        twin = SimpleNamespace(memory_store=SimpleNamespace(get_latest_snapshot=lambda cow_id: snapshot))
        cow_service = SimpleNamespace(_cow_twins={"cow-1": twin})

        self.assertIs(_get_latest_twin_snapshot(cow_service, "cow-1"), snapshot)


if __name__ == "__main__":
    unittest.main()
