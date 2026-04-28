from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.backend_interfaces import (
    MemoryIndexBackend,
    MemoryStoreBackend,
    ProfileStoreBackend,
    SnapshotStoreBackend,
)


@dataclass(slots=True)
class ContextMemoryBackendRegistry:
    memory_store: MemoryStoreBackend | None = None
    profile_store: ProfileStoreBackend | None = None
    snapshot_store: SnapshotStoreBackend | None = None
    memory_index: MemoryIndexBackend | None = None

    def has_memory_store(self) -> bool:
        return self.memory_store is not None

    def has_profile_store(self) -> bool:
        return self.profile_store is not None

    def has_snapshot_store(self) -> bool:
        return self.snapshot_store is not None

    def has_memory_index(self) -> bool:
        return self.memory_index is not None