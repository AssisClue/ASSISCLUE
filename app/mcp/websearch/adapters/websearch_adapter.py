from __future__ import annotations

from dataclasses import dataclass

from app.tools.web_search import search_web


@dataclass(slots=True)
class WebSearchAdapter:
    """
    MCP-facing adapter for web search.

    This keeps MCP independent from the concrete web search helper implementation.
    """

    def search_web(self, *, query: str) -> dict:
        clean_query = str(query or "").strip()
        if not clean_query:
            return {
                "query": clean_query,
                "results": [],
                "count": 0,
                "error": "empty_query",
            }

        results = search_web(clean_query)
        if not isinstance(results, list):
            results = []

        return {
            "query": clean_query,
            "results": results,
            "count": len(results),
        }