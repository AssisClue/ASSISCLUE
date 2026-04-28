from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WebSearchResult:
    query: str
    content: str
    provider: str = "placeholder"
    success: bool = True


def web_search_placeholder(query: str) -> WebSearchResult:
    cleaned = " ".join(query.strip().split())

    return WebSearchResult(
        query=cleaned,
        content=f"WEB SEARCH PLACEHOLDER RESULT for: {cleaned}",
        provider="placeholder",
        success=bool(cleaned),
    )