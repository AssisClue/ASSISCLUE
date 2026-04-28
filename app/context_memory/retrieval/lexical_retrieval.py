from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class LexicalRetrieval:
    def search(
        self,
        query: str,
        items: list[MemoryItem],
        limit: int = 8,
    ) -> list[tuple[float, MemoryItem]]:
        query_words = self._tokenize(query)
        if not query_words:
            ranked = sorted(items, key=lambda item: item.importance, reverse=True)
            return [(item.importance, item) for item in ranked[:limit]]

        scored: list[tuple[float, MemoryItem]] = []

        for item in items:
            item_words = self._tokenize(item.text)
            overlap = len(query_words.intersection(item_words))
            if overlap <= 0:
                continue

            phrase_bonus = 0.5 if query.strip().lower() in item.text.lower() else 0.0
            score = float(overlap) + phrase_bonus + float(item.importance)
            scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:limit]

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.strip(".,!?;:\"'()[]{}").lower()
            for token in text.split()
            if token.strip(".,!?;:\"'()[]{}")
        }