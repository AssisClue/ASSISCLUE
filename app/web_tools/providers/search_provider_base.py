from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class SearchProvider(Protocol):
    def search(self, *, query: str) -> dict:
        ...


@dataclass(slots=True)
class BaseSearchProvider:
    provider_name: str

    def build_result(
        self,
        *,
        query: str,
        url: str,
        title: str,
        items: list[dict] | None = None,
        error: str = "",
    ) -> dict:
        return {
            "provider": self.provider_name,
            "query": str(query or "").strip(),
            "url": str(url or "").strip(),
            "title": str(title or "").strip(),
            "items": list(items or []),
            "count": len(list(items or [])),
            "error": str(error or "").strip(),
        }