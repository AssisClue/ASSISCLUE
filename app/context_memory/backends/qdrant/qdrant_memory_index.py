from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.models.memory_item import MemoryItem

from .qdrant_index_sync_service import QdrantIndexSyncService
from .qdrant_runtime_config import CONTEXT_MEMORY_QDRANT_COLLECTION


@dataclass(slots=True)
class QdrantMemoryIndex:
    collection_name: str = CONTEXT_MEMORY_QDRANT_COLLECTION
    sync_service: QdrantIndexSyncService = field(default_factory=QdrantIndexSyncService)

    def upsert_items(self, items: list[MemoryItem]) -> None:
        # Phase 1 keeps JSON as canonical source of truth.
        # We intentionally do not upsert ad-hoc lists here yet.
        # Use rebuild_from_json() through the sync service.
        _ = items

    def get_all_items(self) -> list[MemoryItem]:
        return self.sync_service.load_memory_items()

    def clear(self) -> None:
        self.sync_service.clear_collection()

    def rebuild_from_json(self) -> dict:
        return self.sync_service.rebuild_from_json()