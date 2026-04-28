from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.retrieval_types import RetrievalQuery, RetrievalResult
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.retrieval.memory_search_service import MemorySearchService


@dataclass(slots=True)
class JsonIndexStore:
    memory_items: list[MemoryItem]
    memory_search_service: MemorySearchService

    def search(self, query: RetrievalQuery) -> list[RetrievalResult]:
        matched_items = self.memory_search_service.search_items(
            query=query.text,
            items=self.memory_items,
            filters=query.filters,
            mode=query.mode,
        )

        results: list[RetrievalResult] = []
        for item in matched_items:
            results.append(
                RetrievalResult(
                    item_id=item.item_id,
                    text=item.text,
                    score=float(item.importance),
                    kind=item.kind,
                    source=item.source,
                    ts=item.ts,
                    metadata=item.metadata,
                )
            )
        return results
    