from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.task_types import TaskType
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot


@dataclass(slots=True)
class TaskContextBuilder:
    def build(
        self,
        task_type: TaskType,
        query: str,
        memory_items: list[MemoryItem],
        live_snapshot: LiveContextSnapshot,
        recent_snapshot: RecentContextSnapshot,
        profile_snapshot: UserProfileSnapshot,
        project_name: str | None = None,
    ) -> TaskContextPacket:
        return TaskContextPacket(
            task_type=task_type,
            query=query,
            summary_lines=self._build_summary_lines(
                task_type=task_type,
                query=query,
                live_snapshot=live_snapshot,
                recent_snapshot=recent_snapshot,
            ),
            memory_items=memory_items[:12],
            recent_items=recent_snapshot.summary_lines[:8],
            profile_items=profile_snapshot.preferences[:6] + profile_snapshot.stable_facts[:6],
            screenshot_notes=live_snapshot.screenshot_notes[:8],
            project_name=project_name,
            metadata={
                "memory_hits": len(memory_items),
                "live_focus": live_snapshot.current_focus,
                "recent_topics": recent_snapshot.recent_topics,
            },
        )

    def _build_summary_lines(
        self,
        task_type: TaskType,
        query: str,
        live_snapshot: LiveContextSnapshot,
        recent_snapshot: RecentContextSnapshot,
    ) -> list[str]:
        lines: list[str] = []

        if live_snapshot.current_focus:
            lines.append(f"Current focus: {live_snapshot.current_focus}")

        lines.extend(recent_snapshot.summary_lines[:4])

        if query.strip():
            lines.append(f"Query: {query.strip()}")

        lines.append(f"Task type: {task_type.value}")
        return lines[:8]