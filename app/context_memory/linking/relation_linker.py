from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.extract.relation_extractor import RelationExtractor
from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class RelationLinker:
    relation_extractor: RelationExtractor

    def link(self, items: list[MemoryItem], min_overlap: int = 2) -> list[MemoryItem]:
        for index, item in enumerate(items):
            related_ids: set[str] = set(item.related_ids)

            for other_index, other in enumerate(items):
                if index == other_index:
                    continue

                if self.relation_extractor.is_related(
                    left_text=item.text,
                    right_text=other.text,
                    min_overlap=min_overlap,
                ):
                    related_ids.add(other.item_id)

            item.related_ids = sorted(related_ids)

        return items