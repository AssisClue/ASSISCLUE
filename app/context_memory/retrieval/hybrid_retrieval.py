from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.retrieval.lexical_retrieval import LexicalRetrieval
from app.context_memory.retrieval.semantic_retrieval import SemanticRetrieval


@dataclass(slots=True)
class HybridRetrieval:
    lexical_retrieval: LexicalRetrieval
    semantic_retrieval: SemanticRetrieval

    def search(
        self,
        query: str,
        items: list[MemoryItem],
        limit: int = 8,
    ) -> list[tuple[float, MemoryItem]]:
        lexical_results = self.lexical_retrieval.search(query=query, items=items, limit=max(limit * 2, 8))
        semantic_results = self.semantic_retrieval.search(query=query, items=items, limit=max(limit * 2, 8))

        merged_scores: dict[str, tuple[float, MemoryItem]] = {}

        for score, item in lexical_results:
            merged_scores[item.item_id] = (score, item)

        for score, item in semantic_results:
            existing = merged_scores.get(item.item_id)
            if existing is None:
                merged_scores[item.item_id] = (score, item)
                continue

            merged_scores[item.item_id] = (existing[0] + score, item)

        merged = list(merged_scores.values())
        merged.sort(key=lambda pair: pair[0], reverse=True)
        return merged[:limit]