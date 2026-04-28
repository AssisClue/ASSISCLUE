from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class ProjectLinker:
    def link(self, items: list[MemoryItem]) -> list[MemoryItem]:
        by_project: dict[str, list[MemoryItem]] = {}

        for item in items:
            if not item.project_name:
                continue
            by_project.setdefault(item.project_name.lower(), []).append(item)

        for project_items in by_project.values():
            project_ids = {item.item_id for item in project_items}
            for item in project_items:
                item.related_ids = sorted(set(item.related_ids).union(project_ids) - {item.item_id})

        return items