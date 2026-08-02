"""Read-only playback helpers for historical digital-twin snapshots.

The playback layer is intentionally additive. It reuses the existing in-memory
snapshot history and reconstructs prior twin states without performing any AI
work or mutating the live twin objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .memory_store import InMemorySnapshotStore
from .snapshot import TwinSnapshot


@dataclass(slots=True)
class PlaybackState:
    """Snapshot of the playback cursor and visible history state.

    Attributes:
        cow_id: The cow whose history is being replayed.
        current_snapshot: The snapshot currently selected for playback.
        playback_position: Zero-based position within the ordered history.
        total_snapshots: Number of snapshots available for the cow.
        started_at: When playback was initialized for the current view.
        playback_mode: Playback mode label for future UI integration.
    """

    cow_id: str
    current_snapshot: TwinSnapshot | None
    playback_position: int = 0
    total_snapshots: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    playback_mode: str = "history"


class PlaybackEngine:
    """Read-only history navigator for digital-twin snapshots.

    The engine never mutates the underlying snapshot store, CowTwin, TwinState,
    timeline entries, or any live AI state. It simply exposes a cursor over the
    previously stored history so future UI layers can render historical states.
    """

    def __init__(self, store: InMemorySnapshotStore, cow_id: str) -> None:
        """Create a playback engine around an existing snapshot store."""
        self.store = store
        self.cow_id = cow_id
        self._history = self.store.list_snapshot_history(cow_id)
        self._position = 0

    def load_snapshot(self, snapshot_id: str) -> PlaybackState | None:
        """Load a specific snapshot by identifier and expose it as playback state."""
        snapshot = self.store.load_snapshot(snapshot_id)
        if snapshot is None:
            return None
        self._history = self.store.list_snapshot_history(self.cow_id)
        self._position = self._find_position(snapshot_id)
        return self._build_state(snapshot)

    def load_latest(self, cow_id: str | None = None) -> PlaybackState | None:
        """Load the latest snapshot for the requested cow without mutating state."""
        resolved_cow_id = cow_id or self.cow_id
        snapshot = self.store.get_latest_snapshot(resolved_cow_id)
        if snapshot is None:
            return None
        self._history = self.store.list_snapshot_history(resolved_cow_id)
        self._position = len(self._history) - 1 if self._history else 0
        return self._build_state(snapshot)

    def playback_at(self, timestamp: datetime) -> PlaybackState | None:
        """Move to the newest snapshot at or before the supplied timestamp."""
        history = self.store.list_snapshot_history(self.cow_id)
        if not history:
            return None
        for index, snapshot in enumerate(reversed(history)):
            if snapshot.timestamp <= timestamp:
                self._history = history
                self._position = len(history) - 1 - index
                return self._build_state(snapshot)
        return self._build_state(history[0])

    def next_snapshot(self) -> PlaybackState | None:
        """Advance to the next snapshot in the ordered history."""
        if not self._history:
            return self._build_state(None)
        if self._position + 1 >= len(self._history):
            return self._build_state(self._history[-1])
        self._position += 1
        return self._build_state(self._history[self._position])

    def previous_snapshot(self) -> PlaybackState | None:
        """Move to the previous snapshot in the ordered history."""
        if not self._history:
            return self._build_state(None)
        if self._position <= 0:
            return self._build_state(self._history[0])
        self._position -= 1
        return self._build_state(self._history[self._position])

    def first_snapshot(self) -> PlaybackState | None:
        """Move to the first snapshot in the ordered history."""
        if not self._history:
            return self._build_state(None)
        self._position = 0
        return self._build_state(self._history[0])

    def last_snapshot(self) -> PlaybackState | None:
        """Move to the last snapshot in the ordered history."""
        if not self._history:
            return self._build_state(None)
        self._position = len(self._history) - 1
        return self._build_state(self._history[-1])

    def current_snapshot(self) -> TwinSnapshot | None:
        """Return the currently selected snapshot without changing state."""
        if not self._history:
            return None
        if self._position < 0:
            self._position = 0
        if self._position >= len(self._history):
            self._position = len(self._history) - 1
        return self._history[self._position]

    def total_snapshots(self) -> int:
        """Return the count of snapshots present in the current cow history."""
        return len(self._history)

    def _find_position(self, snapshot_id: str) -> int:
        """Find the zero-based index of the supplied snapshot identifier."""
        for index, snapshot in enumerate(self._history):
            if snapshot.snapshot_id == snapshot_id:
                return index
        return 0

    def _build_state(self, snapshot: TwinSnapshot | None) -> PlaybackState | None:
        """Construct a playback state object for the given snapshot."""
        return PlaybackState(
            cow_id=self.cow_id,
            current_snapshot=snapshot,
            playback_position=self._position if snapshot is not None else 0,
            total_snapshots=len(self._history),
            started_at=datetime.utcnow(),
            playback_mode="history",
        )
