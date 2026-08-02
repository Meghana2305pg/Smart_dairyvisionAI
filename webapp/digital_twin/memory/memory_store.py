"""Lightweight in-memory repository for digital-twin snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .snapshot import TwinSnapshot


@dataclass(slots=True)
class InMemorySnapshotStore:
    """A small repository that stores immutable snapshots in memory.

    The implementation is intentionally simple so future persistence backends can
    replace it without changing the domain or AI layers. The class preserves
    the legacy methods and adds richer accessors for the Phase 7.1 snapshot
    engine.
    """

    _snapshots: dict[str, TwinSnapshot] = field(default_factory=dict)
    _history: dict[str, list[TwinSnapshot]] = field(default_factory=dict)

    def save_snapshot(self, snapshot: TwinSnapshot) -> None:
        """Persist a snapshot and append it to the cow-specific history."""
        self._snapshots[snapshot.snapshot_id] = snapshot
        self._history.setdefault(snapshot.cow_id, []).append(snapshot)
        self._history[snapshot.cow_id] = sorted(
            self._history[snapshot.cow_id],
            key=lambda item: item.timestamp,
        )

    def load_snapshot(self, snapshot_id: str) -> TwinSnapshot | None:
        """Return a saved snapshot by identifier."""
        return self._snapshots.get(snapshot_id)

    def get_latest_snapshot(self, cow_id: str) -> TwinSnapshot | None:
        """Return the latest snapshot for the requested cow."""
        history = self._history.get(cow_id)
        if not history:
            return None
        return history[-1]

    def list_snapshot_history(self, cow_id: str) -> list[TwinSnapshot]:
        """Return the full ordered history for a cow."""
        return list(self._history.get(cow_id, []))

    def get_latest(self, cow_id: str) -> TwinSnapshot | None:
        """Return the latest snapshot for a cow using the Phase 7.1 accessor."""
        return self.get_latest_snapshot(cow_id)

    def get_snapshot(self, snapshot_id: str) -> TwinSnapshot | None:
        """Return a snapshot by identifier using the new Phase 7.1 accessor."""
        return self.load_snapshot(snapshot_id)

    def get_history(self, cow_id: str) -> list[TwinSnapshot]:
        """Return the ordered history for a cow using the new accessor."""
        return self.list_snapshot_history(cow_id)

    def get_range(self, cow_id: str, start_time: datetime, end_time: datetime) -> list[TwinSnapshot]:
        """Return snapshots for a cow within the supplied inclusive time range."""
        history = self._history.get(cow_id, [])
        if not history:
            return []
        return [item for item in history if start_time <= item.timestamp <= end_time]

    def count(self) -> int:
        """Return the number of stored snapshots."""
        return len(self._snapshots)

    def delete_snapshot(self, snapshot_id: str) -> None:
        """Delete a snapshot by identifier from the store."""
        snapshot = self._snapshots.pop(snapshot_id, None)
        if snapshot is None:
            return
        history = self._history.get(snapshot.cow_id)
        if history is None:
            return
        self._history[snapshot.cow_id] = [item for item in history if item.snapshot_id != snapshot_id]

    def clear(self) -> None:
        """Clear all snapshots from the repository."""
        self._snapshots.clear()
        self._history.clear()
