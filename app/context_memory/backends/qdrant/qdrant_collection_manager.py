from __future__ import annotations

from dataclasses import dataclass, field

from .qdrant_client_adapter import QdrantClientAdapter
from .qdrant_runtime_config import (
    CONTEXT_MEMORY_QDRANT_COLLECTION,
    CONTEXT_MEMORY_QDRANT_DISTANCE,
    CONTEXT_MEMORY_QDRANT_VECTOR_SIZE,
)


@dataclass(slots=True)
class QdrantCollectionManager:
    client_adapter: QdrantClientAdapter = field(default_factory=QdrantClientAdapter)
    collection_name: str = CONTEXT_MEMORY_QDRANT_COLLECTION

    def _resolve_distance(self):
        from qdrant_client.http import models

        mapping = {
            "cosine": models.Distance.COSINE,
            "dot": models.Distance.DOT,
            "euclid": models.Distance.EUCLID,
            "manhattan": models.Distance.MANHATTAN,
        }
        return mapping.get(CONTEXT_MEMORY_QDRANT_DISTANCE, models.Distance.COSINE)

    def ensure_collection(self, collection_name: str | None = None) -> None:
        from qdrant_client.http import models

        client = self.client_adapter.get_client()
        resolved_name = (collection_name or self.collection_name).strip()
        if not resolved_name:
            raise ValueError("Qdrant collection name cannot be empty.")

        if client.collection_exists(resolved_name):
            return

        client.create_collection(
            collection_name=resolved_name,
            vectors_config=models.VectorParams(
                size=int(CONTEXT_MEMORY_QDRANT_VECTOR_SIZE),
                distance=self._resolve_distance(),
            ),
        )

    def has_collection(self, collection_name: str | None = None) -> bool:
        client = self.client_adapter.get_client()
        resolved_name = (collection_name or self.collection_name).strip()
        if not resolved_name:
            return False
        return bool(client.collection_exists(resolved_name))

    def list_collections(self) -> list[str]:
        client = self.client_adapter.get_client()
        result = client.get_collections()
        collections = getattr(result, "collections", []) or []
        names: list[str] = []
        for item in collections:
            name = str(getattr(item, "name", "") or "").strip()
            if name:
                names.append(name)
        return sorted(names)