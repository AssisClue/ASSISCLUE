from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.retrieval_types import RetrievalFilters, RetrievalMode
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.retrieval.hybrid_retrieval import HybridRetrieval
from app.context_memory.retrieval.lexical_retrieval import LexicalRetrieval
from app.context_memory.retrieval.retrieval_filters import RetrievalFilterEngine
from app.context_memory.retrieval.retrieval_ranker import RetrievalRanker
from app.context_memory.retrieval.semantic_retrieval import SemanticRetrieval


@dataclass(slots=True)
class MemorySearchService:
    lexical_retrieval: LexicalRetrieval
    semantic_retrieval: SemanticRetrieval
    hybrid_retrieval: HybridRetrieval
    retrieval_ranker: RetrievalRanker
    retrieval_filter_engine: RetrievalFilterEngine

    def search_items(
        self,
        query: str,
        items: list[MemoryItem],
        filters: RetrievalFilters | None = None,
        mode: RetrievalMode = RetrievalMode.HYBRID,
    ) -> list[MemoryItem]:
        filtered_items = self.retrieval_filter_engine.apply(items=items, filters=filters)
        limit = filters.limit if filters is not None else 8

        if mode == RetrievalMode.LEXICAL:
            scored = self.lexical_retrieval.search(query=query, items=filtered_items, limit=limit)
        elif mode == RetrievalMode.SEMANTIC:
            scored = self.semantic_retrieval.search(query=query, items=filtered_items, limit=limit)
        else:
            scored = self.hybrid_retrieval.search(query=query, items=filtered_items, limit=limit)

        ranked = self.retrieval_ranker.rank(scored_items=scored, limit=limit)
        return [item for _, item in ranked]