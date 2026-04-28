from __future__ import annotations

from typing import Protocol

from app.context_memory.contracts.retrieval_types import RetrievalFilters, RetrievalResult
from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


class ContextMemoryServiceProtocol(Protocol):
    def get_live_context(self) -> LiveContextSnapshot: ...
    def get_recent_context(self) -> RecentContextSnapshot: ...
    def get_user_profile_context(self) -> UserProfileSnapshot: ...
    def get_task_context(
        self,
        task_type: TaskType,
        query: str = "",
        hint: TaskContextHint | None = None,
    ) -> TaskContextPacket: ...
    def search_memory(
        self,
        query: str,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievalResult]: ...