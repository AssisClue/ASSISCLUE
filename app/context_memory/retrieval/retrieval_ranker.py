from __future__ import annotations

import time
from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class RetrievalRanker:
    def rank(
        self,
        scored_items: list[tuple[float, MemoryItem]],
        limit: int = 8,
    ) -> list[tuple[float, MemoryItem]]:
        now = time.time()
        reranked: list[tuple[float, MemoryItem]] = []

        for base_score, item in scored_items:
            recency_bonus = self._recency_bonus(now=now, ts=item.ts)
            final_score = base_score + recency_bonus
            reranked.append((final_score, item))

        reranked.sort(key=lambda pair: pair[0], reverse=True)
        return reranked[:limit]

    def _recency_bonus(self, now: float, ts: float | None) -> float:
        if ts is None:
            return 0.0

        age_seconds = max(now - ts, 0.0)

        if age_seconds <= 60 * 10:
            return 0.75
        if age_seconds <= 60 * 60:
            return 0.50
        if age_seconds <= 60 * 60 * 6:
            return 0.30
        if age_seconds <= 60 * 60 * 24:
            return 0.15
        return 0.0