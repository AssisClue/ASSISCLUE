from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.schemas import MCPToolResult
from app.mcp.websearch.adapters.websearch_adapter import WebSearchAdapter


@dataclass(slots=True)
class WebSearchMCPService:
    """
    MCP-facing web search service.
    """

    adapter: WebSearchAdapter = field(default_factory=WebSearchAdapter)

    def search_web(self, *, query: str) -> MCPToolResult:
        clean_query = str(query or "").strip()
        if not clean_query:
            return MCPToolResult(
                ok=False,
                tool_name="search_web",
                message="Query cannot be empty.",
                error_code="empty_query",
                data={"query": clean_query},
            )

        try:
            data = self.adapter.search_web(query=clean_query)
        except Exception as exc:
            return MCPToolResult(
                ok=False,
                tool_name="search_web",
                message="Web search failed.",
                error_code="web_search_error",
                data={"query": clean_query},
                meta={"exception": f"{type(exc).__name__}: {exc}"},
            )

        return MCPToolResult(
            ok=True,
            tool_name="search_web",
            message="Web search completed.",
            data=data,
            error_code=str(data.get("error") or ""),
        )