from __future__ import annotations

from dataclasses import dataclass, field

from playwright.sync_api import Page

from app.web_tools.providers.search_provider_base import BaseSearchProvider


@dataclass(slots=True)
class GoogleManualProvider(BaseSearchProvider):
    """
    Manual/semi-manual Google route.

    This is intentionally not the default automated search path.
    It only opens Google and optionally pre-fills the query.
    """

    provider_name: str = field(default="google_manual")

    def search(self, *, page: Page, query: str) -> dict:
        clean_query = str(query or "").strip()

        page.goto("https://www.google.com/", wait_until="domcontentloaded")

        if clean_query:
            try:
                page.locator('textarea[name="q"]').fill(clean_query)
            except Exception:
                return self.build_result(
                    query=clean_query,
                    url=page.url,
                    title=page.title(),
                    error="google_prefill_failed",
                )

        return self.build_result(
            query=clean_query,
            url=page.url,
            title=page.title(),
            items=[],
            error="",
        )