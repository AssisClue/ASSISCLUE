from __future__ import annotations

from app.context_memory.backends.qdrant.qdrant_index_sync_service import QdrantIndexSyncService


class QdrantBridge:
    def __init__(self) -> None:
        self.sync_service = QdrantIndexSyncService()

    def rebuild_from_context_memory_json(self) -> dict:
        return self.sync_service.rebuild_from_json()

    def read_status(self) -> dict:
        return self.sync_service.read_index_status()