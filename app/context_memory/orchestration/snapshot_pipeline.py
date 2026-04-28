from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.session.current_activity_state import CurrentActivityState
from app.context_memory.session.session_memory import SessionMemory
from app.context_memory.session.session_window_manager import SessionWindowManager
from app.context_memory.snapshots.live_snapshot_service import LiveSnapshotService
from app.context_memory.snapshots.recent_snapshot_service import RecentSnapshotService


@dataclass(slots=True)
class SnapshotPipeline:
    live_snapshot_service: LiveSnapshotService
    recent_snapshot_service: RecentSnapshotService

    def build_live_snapshot(
        self,
        activity_state: CurrentActivityState,
        session_memory: SessionMemory,
        screenshot_notes: list[str] | None = None,
    ) -> LiveContextSnapshot:
        return self.live_snapshot_service.build_snapshot(
            activity_state=activity_state,
            session_memory=session_memory,
            screenshot_notes=screenshot_notes or [],
        )

    def build_recent_snapshot(
        self,
        window_manager: SessionWindowManager,
        recent_topics: list[str] | None = None,
        recent_projects: list[str] | None = None,
        recent_errors: list[str] | None = None,
    ) -> RecentContextSnapshot:
        return self.recent_snapshot_service.build_snapshot(
            window_manager=window_manager,
            recent_topics=recent_topics or [],
            recent_projects=recent_projects or [],
            recent_errors=recent_errors or [],
        )