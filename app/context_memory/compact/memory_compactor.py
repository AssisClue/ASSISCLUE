from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.normalize.dedupe_keys import build_dedupe_key


@dataclass(slots=True)
class MemoryCompactor:
    def compact(self, items: list[MemoryItem], max_items: int = 200) -> list[MemoryItem]:
        deduped: list[MemoryItem] = []
        seen: set[str] = set()

        for item in items:
            key = build_dedupe_key(text=item.text, source=item.source, kind=item.kind)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        deduped.sort(key=lambda item: (item.importance, item.ts or 0.0), reverse=True)
        return deduped[:max_items]