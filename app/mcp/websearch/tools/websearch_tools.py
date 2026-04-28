from __future__ import annotations

from app.mcp.websearch.services.websearch_mcp_service import WebSearchMCPService


def register_websearch_tools(server) -> None:
    service = WebSearchMCPService()

    server.register_tool(
        name="search_web",
        description="Run a web search using the existing app web search helper.",
        handler=service.search_web,
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
        tags=["websearch", "web", "read"],
    )