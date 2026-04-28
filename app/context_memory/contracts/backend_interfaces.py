from __future__ import annotations

from typing import Protocol

from app.context_memory.contracts.retrieval_types import RetrievalQuery, RetrievalResult
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


class MemoryStoreBackend(Protocol):
    def save_memory_items(self, items: list[MemoryItem]) -> None: ...
    def load_memory_items(self) -> list[MemoryItem]: ...


class ProfileStoreBackend(Protocol):
    def save_user_profile_snapshot(self, snapshot: UserProfileSnapshot) -> None: ...
    def load_user_profile_snapshot(self) -> UserProfileSnapshot | None: ...


class SnapshotStoreBackend(Protocol):
    def save_live_context_snapshot(self, snapshot: LiveContextSnapshot) -> None: ...
    def load_live_context_snapshot(self) -> LiveContextSnapshot | None: ...
    def save_recent_context_snapshot(self, snapshot: RecentContextSnapshot) -> None: ...
    def load_recent_context_snapshot(self) -> RecentContextSnapshot | None: ...


class MemoryIndexBackend(Protocol):
    def search(self, query: RetrievalQuery) -> list[RetrievalResult]: ...