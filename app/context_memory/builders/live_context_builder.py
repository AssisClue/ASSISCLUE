from __future__ import annotations

import time
from dataclasses import dataclass

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.session.current_activity_state import CurrentActivityState
from app.context_memory.session.session_memory import SessionMemory


@dataclass(slots=True)
class LiveContextBuilder:
    def build(
        self,
        activity_state: CurrentActivityState,
        session_memory: SessionMemory,
        screenshot_notes: list[str] | None = None,
    ) -> LiveContextSnapshot:
        recent_events = session_memory.get_recent_texts(limit=12)

        return LiveContextSnapshot(
            current_focus=activity_state.current_focus or activity_state.active_task,
            active_topics=list(activity_state.active_topics),
            recent_events=recent_events,
            screenshot_notes=list(screenshot_notes or []),
            open_issues=list(activity_state.open_issues),
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.LIVE,
                ts=time.time(),
                source_count=1,
                item_count=len(recent_events),
                tags=list(activity_state.active_topics),
            ),
            extra={
                "active_project": activity_state.active_project,
                "last_user_text": activity_state.last_user_text,
                "last_assistant_text": activity_state.last_assistant_text,
            },
        )