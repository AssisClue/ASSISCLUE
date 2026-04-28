from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.contracts.task_types import TaskType


@dataclass(slots=True)
class ProjectContextBuilder:
    def build(self, project_name: str, items: list[MemoryItem]) -> TaskContextPacket:
        project_items = [
            item for item in items
            if item.project_name and item.project_name.lower() == project_name.strip().lower()
        ]

        return TaskContextPacket(
            task_type=TaskType.PROJECT_FOLLOWUP,
            query=project_name,
            summary_lines=[item.text for item in project_items[:8]],
            memory_items=project_items[:12],
            project_name=project_name,
            metadata={"memory_hits": len(project_items)},
        )