from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.retrieval.task_context_retrieval import TaskContextRetrieval


@dataclass(slots=True)
class RetrievalPipeline:
    task_context_retrieval: TaskContextRetrieval

    def run_for_task(
        self,
        task_type: TaskType,
        query: str,
        items: list[MemoryItem],
        hint: TaskContextHint | None = None,
    ) -> list[MemoryItem]:
        return self.task_context_retrieval.search_for_task(
            task_type=task_type,
            query=query,
            items=items,
            hint=hint,
        )