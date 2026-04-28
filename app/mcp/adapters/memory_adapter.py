from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.services.context_memory_service import ContextMemoryService
from app.context_memory.user_spaces.user_spaces_service import UserSpacesService


def _to_plain_data(value: Any) -> Any:
    """
    Best-effort converter for dataclass-like or model-like values into
    MCP-friendly plain Python structures.
    """
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, dict):
        return {str(key): _to_plain_data(val) for key, val in value.items()}

    if hasattr(value, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for field_name in value.__dataclass_fields__.keys():
            result[field_name] = _to_plain_data(getattr(value, field_name))
        return result

    if hasattr(value, "__dict__"):
        raw = vars(value)
        return {str(key): _to_plain_data(val) for key, val in raw.items()}

    return str(value)


@dataclass(slots=True)
class MemoryAdapter:
    """
    MCP-facing adapter for context memory and user spaces.

    Important:
    - uses service layer
    - does not talk directly to Mem0, Qdrant, or raw stores
    """

    context_memory_service: ContextMemoryService = field(default_factory=ContextMemoryService.create_default)
    user_spaces_service: UserSpacesService = field(default_factory=UserSpacesService.create_default)

    def search_memory(
        self,
        *,
        query: str,
        limit: int = 5,
        preferred_sources: list[str] | None = None,
    ) -> dict[str, Any]:
        clean_query = str(query or "").strip()
        clean_limit = max(1, int(limit or 5))

        hint = TaskContextHint(preferred_sources=list(preferred_sources or []))
        answer = self.context_memory_service.answer_memory_query(
            clean_query,
            limit=clean_limit,
            hint=hint,
        )

        return {
            "query": clean_query,
            "limit": clean_limit,
            "memory_hits": answer.memory_hits,
            "matches": list(answer.matches),
            "summary_lines": list(answer.summary_lines),
            "fallback_reason": answer.fallback_reason,
            "preferred_sources": list(preferred_sources or []),
        }

    def get_recent_context(self) -> dict[str, Any]:
        snapshot = self.context_memory_service.get_recent_context()
        return _to_plain_data(snapshot)

    def get_live_context(self) -> dict[str, Any]:
        snapshot = self.context_memory_service.get_live_context()
        return _to_plain_data(snapshot)

    def get_user_profile_context(self) -> dict[str, Any]:
        snapshot = self.context_memory_service.get_user_profile_context()
        return _to_plain_data(snapshot)

    def get_task_context(
        self,
        *,
        task_type: str,
        query: str = "",
        project_name: str = "",
        preferred_sources: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        resolved_task_type = TaskType(task_type)
        hint = TaskContextHint(
            project_name=str(project_name or "").strip() or None,
            preferred_sources=list(preferred_sources or []),
            tags=list(tags or []),
        )

        packet = self.context_memory_service.get_task_context(
            task_type=resolved_task_type,
            query=str(query or "").strip(),
            hint=hint,
        )
        return _to_plain_data(packet)

    def list_user_spaces(self) -> list[str]:
        return self.user_spaces_service.list_spaces()

    def get_user_space(
        self,
        *,
        space_id: str,
        query: str = "",
        limit: int = 20,
    ) -> dict[str, Any]:
        clean_space_id = str(space_id or "").strip()
        clean_query = str(query or "").strip()
        clean_limit = max(1, int(limit or 20))

        items = self.user_spaces_service.search(
            query=clean_query,
            space_ids=[clean_space_id],
            limit=clean_limit,
        )

        return {
            "space_id": clean_space_id,
            "query": clean_query,
            "limit": clean_limit,
            "items": _to_plain_data(items),
        }