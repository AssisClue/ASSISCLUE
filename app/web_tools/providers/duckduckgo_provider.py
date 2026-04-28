from __future__ import annotations

from dataclasses import dataclass, field

from playwright.sync_api import Page

from app.web_tools.providers.search_provider_base import BaseSearchProvider


@dataclass(slots=True)
class DuckDuckGoSearchProvider(BaseSearchProvider):
    """
    Browser-based simple search provider for DuckDuckGo.

    Phase 1:
    - visible browser flow
    - no result parsing yet
    - enough to confirm search works without Google captcha path
    """

    provider_name: str = field(default="duckduckgo")

    def search(self, *, page: Page, query: str) -> dict:
        clean_query = str(query or "").strip()
        if not clean_query:
            return self.build_result(
                query=clean_query,
                url="",
                title="",
                error="empty_query",
            )

        page.goto("https://duckduckgo.com/", wait_until="domcontentloaded")
        page.locator('input[name="q"]').fill(clean_query)
        page.locator('input[name="q"]').press("Enter")
        page.wait_for_load_state("domcontentloaded")

        return self.build_result(
            query=clean_query,
            url=page.url,
            title=page.title(),
            items=[],
            error="",
        )