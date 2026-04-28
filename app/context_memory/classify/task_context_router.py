from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.retrieval_types import RetrievalFilters
from app.context_memory.contracts.task_types import TaskContextHint, TaskType


@dataclass(slots=True)
class TaskContextRouter:
    def build_filters(
        self,
        task_type: TaskType,
        hint: TaskContextHint | None = None,
    ) -> RetrievalFilters:
        resolved_hint = hint or TaskContextHint()
        filters = RetrievalFilters(limit=8)

        if task_type == TaskType.SCREENSHOT_ANALYSIS:
            filters.kinds = ["screenshot_context", "issue", "general_memory"]
            filters.sources = ["screenshot_note", "session_event", "chat_history"]

        elif task_type == TaskType.SCREENSHOT_CODE:
            filters.kinds = ["coding_issue", "file_context", "project_context", "issue"]
            filters.sources = ["screenshot_note", "file_context", "session_event", "chat_history"]

        elif task_type == TaskType.CODING_HELP:
            filters.kinds = ["coding_issue", "file_context", "project_context"]
            filters.sources = ["file_context", "session_event", "chat_history"]

        elif task_type == TaskType.TIMELINE_LOOKUP:
            filters.kinds = ["timeline", "general_memory", "persistent_fact"]
            filters.sources = ["session_event", "chat_history", "runtime_state"]

        elif task_type == TaskType.MEETING_LOOKUP:
            filters.kinds = ["timeline", "general_memory"]
            filters.sources = ["session_event", "chat_history"]

        elif task_type == TaskType.PROJECT_FOLLOWUP:
            filters.kinds = ["project_context", "issue", "general_memory", "file_context"]
            filters.sources = ["file_context", "session_event", "chat_history"]

        elif task_type == TaskType.USER_PREFERENCE:
            filters.kinds = ["preference", "persistent_fact"]
            filters.sources = ["chat_history", "session_event"]

        elif task_type == TaskType.MEMORY_SEARCH:
            filters.limit = 12

        if resolved_hint.project_name:
            filters.project_names = [resolved_hint.project_name]

        if resolved_hint.preferred_sources:
            filters.sources = resolved_hint.preferred_sources

        if resolved_hint.tags:
            filters.tags = resolved_hint.tags

        return filters