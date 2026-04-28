from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class TimelineLinker:
    timeline_kinds: tuple[str, ...] = ("timeline", "issue", "coding_issue")

    def link(self, items: list[MemoryItem], max_gap_seconds: float = 60 * 60 * 6) -> list[MemoryItem]:
        timeline_items = [
            item for item in items
            if item.kind in self.timeline_kinds and item.ts is not None
        ]
        timeline_items.sort(key=lambda item: float(item.ts or 0.0))

        for index, item in enumerate(timeline_items):
            related_ids: set[str] = set(item.related_ids)

            for other_index, other in enumerate(timeline_items):
                if index == other_index:
                    continue
                if other.ts is None or item.ts is None:
                    continue

                if abs(other.ts - item.ts) <= max_gap_seconds:
                    related_ids.add(other.item_id)

            item.related_ids = sorted(related_ids)

        return items