from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.normalize.dedupe_keys import build_dedupe_key


@dataclass(slots=True)
class DuplicateLinker:
    def link_duplicates(self, items: list[MemoryItem]) -> list[MemoryItem]:
        grouped: dict[str, list[MemoryItem]] = {}

        for item in items:
            key = build_dedupe_key(text=item.text, source=item.source, kind=item.kind)
            grouped.setdefault(key, []).append(item)

        for duplicates in grouped.values():
            if len(duplicates) <= 1:
                continue

            duplicate_ids = sorted({item.item_id for item in duplicates})
            for item in duplicates:
                item.related_ids = sorted(set(item.related_ids).union(duplicate_ids) - {item.item_id})

        return items