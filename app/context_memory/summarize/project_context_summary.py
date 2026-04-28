from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class ProjectContextSummary:
    def build_lines(
        self,
        project_name: str,
        items: list[MemoryItem],
        max_items: int = 10,
    ) -> list[str]:
        lowered_project = project_name.strip().lower()
        if not lowered_project:
            return []

        project_items = [
            item for item in items
            if item.project_name and item.project_name.lower() == lowered_project
        ]
        project_items.sort(key=lambda item: (item.importance, item.ts or 0.0), reverse=True)

        lines: list[str] = []
        for item in project_items[:max_items]:
            lines.append(item.text)

        return lines