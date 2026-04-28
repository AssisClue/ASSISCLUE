from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Mem0Adapter:
    client: Any | None = None
    user_id: str = "default_user"
    enabled: bool = False
    _fallback_items: list[dict[str, Any]] = field(default_factory=list)

    def is_ready(self) -> bool:
        return self.enabled and self.client is not None

    def add(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        payload = {
            "text": text.strip(),
            "metadata": dict(metadata or {}),
            "user_id": self.user_id,
        }
        if not payload["text"]:
            return

        if self.is_ready():
            self.client.add(payload["text"], user_id=self.user_id, metadata=payload["metadata"])
            return

        self._fallback_items.append(payload)

    def search(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        cleaned_query = query.strip().lower()
        if not cleaned_query:
            return self._fallback_items[:limit]

        if self.is_ready():
            result = self.client.search(query=query, user_id=self.user_id, limit=limit)
            if isinstance(result, list):
                return result
            return []

        query_words = {word for word in cleaned_query.split() if word}
        scored: list[tuple[int, dict[str, Any]]] = []

        for item in self._fallback_items:
            text = str(item.get("text") or "")
            text_words = {word.lower() for word in text.split() if word.strip()}
            overlap = len(query_words.intersection(text_words))
            if overlap > 0:
                scored.append((overlap, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def dump_all(self) -> list[dict[str, Any]]:
        return list(self._fallback_items)