from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.summarize.project_context_summary import ProjectContextSummary


@dataclass(slots=True)
class ProjectSnapshotService:
    project_context_summary: ProjectContextSummary

    def build_project_lines(
        self,
        project_name: str,
        items: list[MemoryItem],
        max_items: int = 10,
    ) -> list[str]:
        return self.project_context_summary.build_lines(
            project_name=project_name,
            items=items,
            max_items=max_items,
        )