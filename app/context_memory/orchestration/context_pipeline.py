from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.builders.context_packet_builder import ContextPacketBuilder
from app.context_memory.builders.task_context_builder import TaskContextBuilder
from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


@dataclass(slots=True)
class ContextPipeline:
    task_context_builder: TaskContextBuilder
    context_packet_builder: ContextPacketBuilder

    def build_task_packet(
        self,
        task_type: TaskType,
        query: str,
        memory_items: list[MemoryItem],
        live_snapshot: LiveContextSnapshot,
        recent_snapshot: RecentContextSnapshot,
        profile_snapshot: UserProfileSnapshot,
        hint: TaskContextHint | None = None,
    ) -> TaskContextPacket:
        resolved_hint = hint or TaskContextHint()

        return self.task_context_builder.build(
            task_type=task_type,
            query=query,
            memory_items=memory_items,
            live_snapshot=live_snapshot,
            recent_snapshot=recent_snapshot,
            profile_snapshot=profile_snapshot,
            project_name=resolved_hint.project_name,
        )

    def build_context_packet_dict(
        self,
        live_snapshot: LiveContextSnapshot,
        recent_snapshot: RecentContextSnapshot,
        profile_snapshot: UserProfileSnapshot,
        task_packet: TaskContextPacket,
    ) -> dict:
        return self.context_packet_builder.build_packet(
            live_snapshot=live_snapshot,
            recent_snapshot=recent_snapshot,
            profile_snapshot=profile_snapshot,
            task_packet=task_packet,
        )