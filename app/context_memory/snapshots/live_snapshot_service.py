from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.builders.live_context_builder import LiveContextBuilder
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.session.current_activity_state import CurrentActivityState
from app.context_memory.session.session_memory import SessionMemory


@dataclass(slots=True)
class LiveSnapshotService:
    live_context_builder: LiveContextBuilder

    def build_snapshot(
        self,
        activity_state: CurrentActivityState,
        session_memory: SessionMemory,
        screenshot_notes: list[str] | None = None,
    ) -> LiveContextSnapshot:
        return self.live_context_builder.build(
            activity_state=activity_state,
            session_memory=session_memory,
            screenshot_notes=screenshot_notes or [],
        )