from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5
import json
import time

from app.context_memory.backends.json.json_memory_store import JsonMemoryStore
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.runtime.storage_paths import ContextMemoryStoragePaths

from .qdrant_client_adapter import QdrantClientAdapter
from .qdrant_runtime_config import (
    CONTEXT_MEMORY_QDRANT_COLLECTION,
    CONTEXT_MEMORY_QDRANT_DISTANCE,
    CONTEXT_MEMORY_QDRANT_SCHEMA_VERSION,
    CONTEXT_MEMORY_QDRANT_VECTOR_SIZE,
)
from .qdrant_text_embedder import QdrantTextEmbedder


@dataclass(slots=True)
class QdrantIndexSyncService:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[4])
    collection_name: str = CONTEXT_MEMORY_QDRANT_COLLECTION
    client_adapter: QdrantClientAdapter = field(default_factory=QdrantClientAdapter)
    embedder: QdrantTextEmbedder = field(default_factory=QdrantTextEmbedder)

    def _runtime_root(self) -> Path:
        return self.project_root / "runtime"

    def _storage_paths(self) -> ContextMemoryStoragePaths:
        return ContextMemoryStoragePaths(runtime_root=self._runtime_root())

    def _memory_store(self) -> JsonMemoryStore:
        paths = self._storage_paths()
        paths.ensure_directories()
        return JsonMemoryStore(storage_path=paths.memory_items_path)

    def _metadata_path(self) -> Path:
        path = self._runtime_root() / "status" / "memory" / "qdrant_index_status.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _point_id(self, item: MemoryItem) -> str:
        return str(uuid5(NAMESPACE_URL, f"context-memory:{item.item_id}"))

    def _resolve_distance(self):
        from qdrant_client.http import models

        mapping = {
            "cosine": models.Distance.COSINE,
            "dot": models.Distance.DOT,
            "euclid": models.Distance.EUCLID,
            "manhattan": models.Distance.MANHATTAN,
        }
        return mapping.get(CONTEXT_MEMORY_QDRANT_DISTANCE, models.Distance.COSINE)

    def _payload(self, item: MemoryItem) -> dict[str, Any]:
        return {
            "item_id": item.item_id,
            "text": item.text,
            "kind": item.kind,
            "source": item.source,
            "ts": item.ts,
            "importance": item.importance,
            "tags": list(item.tags),
            "project_name": str(getattr(item, "project_name", "") or "").strip(),
            "metadata": dict(item.metadata),
        }

    def ensure_collection(self) -> None:
        from qdrant_client.http import models

        client = self.client_adapter.get_client()
        if client.collection_exists(self.collection_name):
            return

        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=int(CONTEXT_MEMORY_QDRANT_VECTOR_SIZE),
                distance=self._resolve_distance(),
            ),
        )

    def clear_collection(self) -> None:
        client = self.client_adapter.get_client()
        if client.collection_exists(self.collection_name):
            client.delete_collection(self.collection_name)
        self.ensure_collection()

    def load_memory_items(self) -> list[MemoryItem]:
        return self._memory_store().load_memory_items()

    def rebuild_from_json(self) -> dict[str, Any]:
        from qdrant_client.http import models

        items = self.load_memory_items()
        self.clear_collection()
        client = self.client_adapter.get_client()

        points: list[models.PointStruct] = []
        for item in items:
            points.append(
                models.PointStruct(
                    id=self._point_id(item),
                    vector=self.embedder.embed_text(item.text),
                    payload=self._payload(item),
                )
            )

        if points:
            client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True,
            )

        payload = {
            "ok": True,
            "updated_at": time.time(),
            "collection_name": self.collection_name,
            "item_count": len(items),
            "vector_size": int(CONTEXT_MEMORY_QDRANT_VECTOR_SIZE),
            "distance": CONTEXT_MEMORY_QDRANT_DISTANCE,
            "schema_version": str(CONTEXT_MEMORY_QDRANT_SCHEMA_VERSION),
            "index_backend": "qdrant",
            "source_of_truth": "json",
        }
        self._metadata_path().write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def read_index_status(self) -> dict[str, Any]:
        path = self._metadata_path()
        if not path.exists() or not path.is_file():
            return {}
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return raw if isinstance(raw, dict) else {}
