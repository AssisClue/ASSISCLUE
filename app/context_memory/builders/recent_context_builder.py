from __future__ import annotations

import time
from dataclasses import dataclass

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.session.session_window_manager import SessionWindowManager


@dataclass(slots=True)
class RecentContextBuilder:
    def build(
        self,
        window_manager: SessionWindowManager,
        recent_topics: list[str] | None = None,
        recent_projects: list[str] | None = None,
        recent_errors: list[str] | None = None,
    ) -> RecentContextSnapshot:
        recent_events = window_manager.get_recent_texts(limit=20)

        return RecentContextSnapshot(
            summary_lines=recent_events[:12],
            recent_topics=list(recent_topics or []),
            recent_projects=list(recent_projects or []),
            notable_events=recent_events[:8],
            recent_errors=list(recent_errors or []),
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.RECENT,
                ts=time.time(),
                source_count=1,
                item_count=len(recent_events),
                tags=list(recent_topics or []),
            ),
        )