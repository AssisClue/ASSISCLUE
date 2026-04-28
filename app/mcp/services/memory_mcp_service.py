from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.mcp.adapters.memory_adapter import MemoryAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class MemoryMCPService:
    """
    MCP-facing memory service.

    Responsibilities:
    - validate and normalize MCP-style inputs
    - delegate actual memory access to MemoryAdapter
    - return normalized MCPToolResult objects
    """

    adapter: MemoryAdapter = field(default_factory=MemoryAdapter)

    def search_memory(
        self,
        *,
        query: str,
        limit: int = 5,
        preferred_sources: list[str] | None = None,
    ) -> MCPToolResult:
        clean_query = str(query or "").strip()
        clean_limit = max(1, int(limit or 5))
        clean_sources = [str(value).strip() for value in (preferred_sources or []) if str(value).strip()]

        if not clean_query:
            return MCPToolResult(
                ok=False,
                tool_name="search_memory",
                message="Query cannot be empty.",
                error_code="empty_query",
                data={
                    "query": clean_query,
                    "limit": clean_limit,
                    "preferred_sources": clean_sources,
                },
            )

        data = self.adapter.search_memory(
            query=clean_query,
            limit=clean_limit,
            preferred_sources=clean_sources,
        )
        return MCPToolResult(
            ok=True,
            tool_name="search_memory",
            message="Memory search completed.",
            data=data,
            meta={"preferred_sources": clean_sources},
        )

    def get_recent_context(self) -> MCPToolResult:
        data = self.adapter.get_recent_context()
        return MCPToolResult(
            ok=True,
            tool_name="get_recent_context",
            message="Recent context loaded.",
            data=data,
        )

    def get_live_context(self) -> MCPToolResult:
        data = self.adapter.get_live_context()
        return MCPToolResult(
            ok=True,
            tool_name="get_live_context",
            message="Live context loaded.",
            data=data,
        )

    def get_user_profile_context(self) -> MCPToolResult:
        data = self.adapter.get_user_profile_context()
        return MCPToolResult(
            ok=True,
            tool_name="get_user_profile_context",
            message="User profile context loaded.",
            data=data,
        )

    def get_task_context(
        self,
        *,
        task_type: str,
        query: str = "",
        project_name: str = "",
        preferred_sources: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> MCPToolResult:
        clean_task_type = str(task_type or "").strip()
        clean_query = str(query or "").strip()
        clean_project_name = str(project_name or "").strip()
        clean_sources = [str(value).strip() for value in (preferred_sources or []) if str(value).strip()]
        clean_tags = [str(value).strip() for value in (tags or []) if str(value).strip()]

        if not clean_task_type:
            return MCPToolResult(
                ok=False,
                tool_name="get_task_context",
                message="Task type cannot be empty.",
                error_code="empty_task_type",
                data={
                    "task_type": clean_task_type,
                    "query": clean_query,
                    "project_name": clean_project_name,
                    "preferred_sources": clean_sources,
                    "tags": clean_tags,
                },
            )

        try:
            data = self.adapter.get_task_context(
                task_type=clean_task_type,
                query=clean_query,
                project_name=clean_project_name,
                preferred_sources=clean_sources,
                tags=clean_tags,
            )
        except Exception as exc:
            return MCPToolResult(
                ok=False,
                tool_name="get_task_context",
                message="Task context failed.",
                error_code="task_context_error",
                data={
                    "task_type": clean_task_type,
                    "query": clean_query,
                    "project_name": clean_project_name,
                    "preferred_sources": clean_sources,
                    "tags": clean_tags,
                },
                meta={"exception": f"{type(exc).__name__}: {exc}"},
            )

        return MCPToolResult(
            ok=True,
            tool_name="get_task_context",
            message="Task context loaded.",
            data=data,
            meta={
                "task_type": clean_task_type,
                "preferred_sources": clean_sources,
                "tags": clean_tags,
            },
        )

    def list_user_spaces(self) -> MCPToolResult:
        spaces = self.adapter.list_user_spaces()
        return MCPToolResult(
            ok=True,
            tool_name="list_user_spaces",
            message="User spaces loaded.",
            data={"spaces": spaces, "count": len(spaces)},
        )

    def get_user_space(
        self,
        *,
        space_id: str,
        query: str = "",
        limit: int = 20,
    ) -> MCPToolResult:
        clean_space_id = str(space_id or "").strip()
        clean_query = str(query or "").strip()
        clean_limit = max(1, int(limit or 20))

        if not clean_space_id:
            return MCPToolResult(
                ok=False,
                tool_name="get_user_space",
                message="Space id cannot be empty.",
                error_code="empty_space_id",
                data={
                    "space_id": clean_space_id,
                    "query": clean_query,
                    "limit": clean_limit,
                },
            )

        data = self.adapter.get_user_space(
            space_id=clean_space_id,
            query=clean_query,
            limit=clean_limit,
        )
        return MCPToolResult(
            ok=True,
            tool_name="get_user_space",
            message="User space loaded.",
            data=data,
        )