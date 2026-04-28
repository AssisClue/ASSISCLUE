from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.retrieval_types import RetrievalFilters
from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class RetrievalFilterEngine:
    def apply(
        self,
        items: list[MemoryItem],
        filters: RetrievalFilters | None,
    ) -> list[MemoryItem]:
        if filters is None:
            return list(items)

        filtered = list(items)

        if filters.kinds:
            allowed_kinds = {value.lower() for value in filters.kinds}
            filtered = [item for item in filtered if item.kind.lower() in allowed_kinds]

        if filters.sources:
            allowed_sources = {value.lower() for value in filters.sources}
            filtered = [item for item in filtered if item.source.lower() in allowed_sources]

        if filters.project_names:
            allowed_projects = {value.lower() for value in filters.project_names}
            filtered = [
                item for item in filtered
                if item.project_name and item.project_name.lower() in allowed_projects
            ]

        if filters.tags:
            wanted_tags = {value.lower() for value in filters.tags}
            filtered = [
                item for item in filtered
                if wanted_tags.intersection({tag.lower() for tag in item.tags})
            ]

        if filters.min_ts is not None:
            filtered = [
                item for item in filtered
                if item.ts is not None and item.ts >= filters.min_ts
            ]

        if filters.max_ts is not None:
            filtered = [
                item for item in filtered
                if item.ts is not None and item.ts <= filters.max_ts
            ]

        return filtered