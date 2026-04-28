from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.builders.recent_context_builder import RecentContextBuilder
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.session.session_window_manager import SessionWindowManager


@dataclass(slots=True)
class RecentSnapshotService:
    recent_context_builder: RecentContextBuilder

    def build_snapshot(
        self,
        window_manager: SessionWindowManager,
        recent_topics: list[str] | None = None,
        recent_projects: list[str] | None = None,
        recent_errors: list[str] | None = None,
    ) -> RecentContextSnapshot:
        return self.recent_context_builder.build(
            window_manager=window_manager,
            recent_topics=recent_topics or [],
            recent_projects=recent_projects or [],
            recent_errors=recent_errors or [],
        )