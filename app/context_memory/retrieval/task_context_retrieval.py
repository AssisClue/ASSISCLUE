from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.classify.task_context_router import TaskContextRouter
from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.retrieval.memory_search_service import MemorySearchService


@dataclass(slots=True)
class TaskContextRetrieval:
    memory_search_service: MemorySearchService
    task_context_router: TaskContextRouter

    def search_for_task(
        self,
        task_type: TaskType,
        query: str,
        items: list[MemoryItem],
        hint: TaskContextHint | None = None,
    ) -> list[MemoryItem]:
        filters = self.task_context_router.build_filters(task_type=task_type, hint=hint)
        return self.memory_search_service.search_items(
            query=query,
            items=items,
            filters=filters,
        )