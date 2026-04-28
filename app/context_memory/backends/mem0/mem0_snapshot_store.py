from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot


@dataclass(slots=True)
class Mem0SnapshotStore:
    live_snapshot: LiveContextSnapshot | None = None
    recent_snapshot: RecentContextSnapshot | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def save_live_context_snapshot(self, snapshot: LiveContextSnapshot) -> None:
        self.live_snapshot = snapshot

    def load_live_context_snapshot(self) -> LiveContextSnapshot | None:
        if self.live_snapshot is None:
            return LiveContextSnapshot(
                metadata=ContextSnapshotMetadata(kind=ContextKind.LIVE, ts=0.0)
            )
        return self.live_snapshot

    def save_recent_context_snapshot(self, snapshot: RecentContextSnapshot) -> None:
        self.recent_snapshot = snapshot

    def load_recent_context_snapshot(self) -> RecentContextSnapshot | None:
        if self.recent_snapshot is None:
            return RecentContextSnapshot(
                metadata=ContextSnapshotMetadata(kind=ContextKind.RECENT, ts=0.0)
            )
        return self.recent_snapshot