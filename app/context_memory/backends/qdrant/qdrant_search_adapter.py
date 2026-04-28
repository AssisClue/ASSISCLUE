from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.contracts.retrieval_types import RetrievalFilters, RetrievalResult

from .qdrant_memory_index import QdrantMemoryIndex
from .qdrant_text_embedder import QdrantTextEmbedder


@dataclass(slots=True)
class QdrantSearchAdapter:
    qdrant_memory_index: QdrantMemoryIndex
    embedder: QdrantTextEmbedder = field(default_factory=QdrantTextEmbedder)

    def _passes_filters(self, result: RetrievalResult, filters: RetrievalFilters | None) -> bool:
        if filters is None:
            return True

        if filters.kinds:
            allowed = {value.lower() for value in filters.kinds}
            if result.kind.lower() not in allowed:
                return False

        if filters.sources:
            allowed_raw = {str(value).strip().lower() for value in filters.sources if str(value).strip()}
            allowed_exact = {value for value in allowed_raw if not value.endswith(".*")}
            allowed_prefixes = [value[:-1] for value in allowed_raw if value.endswith(".*")]

            src = result.source.lower()
            if src not in allowed_exact and not any(src.startswith(prefix) for prefix in allowed_prefixes):
                return False

        if filters.project_names:
            project_name = str((result.metadata or {}).get("project_name", "") or "").strip().lower()
            allowed = {value.lower() for value in filters.project_names}
            if not project_name or project_name not in allowed:
                return False

        if filters.tags:
            wanted = {value.lower() for value in filters.tags}
            tags = {str(tag).lower() for tag in ((result.metadata or {}).get("tags", []) or [])}
            if not wanted.intersection(tags):
                return False

        if filters.min_ts is not None:
            if result.ts is None or result.ts < filters.min_ts:
                return False

        if filters.max_ts is not None:
            if result.ts is None or result.ts > filters.max_ts:
                return False

        return True

    def search_text(
        self,
        *,
        query: str,
        limit: int = 8,
        filters: RetrievalFilters | None = None,
    ) -> list[RetrievalResult]:
        clean_query = str(query or "").strip()
        if not clean_query:
            return []

        index = self.qdrant_memory_index
        client = index.sync_service.client_adapter.get_client()
        index.sync_service.ensure_collection()

        response = client.query_points(
            collection_name=index.collection_name,
            query=self.embedder.embed_text(clean_query),
            with_payload=True,
            limit=max(1, int(limit)),
        )

        points = getattr(response, "points", []) or []
        results: list[RetrievalResult] = []

        for point in points:
            payload = dict(getattr(point, "payload", {}) or {})
            metadata = dict(payload.get("metadata", {}) or {})
            metadata.setdefault("tags", list(payload.get("tags", []) or []))
            metadata.setdefault("project_name", str(payload.get("project_name", "") or "").strip())

            result = RetrievalResult(
                item_id=str(payload.get("item_id", "") or "").strip(),
                text=str(payload.get("text", "") or "").strip(),
                score=float(getattr(point, "score", 0.0) or 0.0),
                kind=str(payload.get("kind", "") or "").strip(),
                source=str(payload.get("source", "") or "").strip(),
                ts=payload.get("ts"),
                metadata=metadata,
            )
            if self._passes_filters(result, filters):
                results.append(result)

        return results[: max(1, int(limit))]