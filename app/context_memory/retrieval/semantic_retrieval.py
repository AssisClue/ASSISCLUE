from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class SemanticRetrieval:
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
            text_words = self._tokenize(item.text)
            tag_words = {tag.lower() for tag in item.tags}
            project_words = {item.project_name.lower()} if item.project_name else set()

            overlap_text = len(query_words.intersection(text_words))
            overlap_tags = len(query_words.intersection(tag_words))
            overlap_project = len(query_words.intersection(project_words))

            score = (
                float(overlap_text) * 1.0
                + float(overlap_tags) * 1.5
                + float(overlap_project) * 2.0
                + float(item.importance) * 0.75
            )

            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[:limit]

    def _tokenize(self, text: str) -> set[str]:
        return {
            token.strip(".,!?;:\"'()[]{}").lower()
            for token in text.split()
            if token.strip(".,!?;:\"'()[]{}")
        }