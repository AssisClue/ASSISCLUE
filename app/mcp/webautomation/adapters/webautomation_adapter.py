from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.web_tools.browser.extractors import (
    get_page_text,
    get_page_title,
    save_page_html,
    save_page_text,
)
from app.web_tools.browser.navigation import (
    click_locator,
    open_url,
    press_key,
    type_into_locator,
    wait_ms,
)
from app.web_tools.browser.playwright_manager import (
    PlaywrightManager,
    PlaywrightSession,
    get_shared_playwright_manager,
)
from app.web_tools.browser.browser_service_client import call_browser_service
from app.web_tools.browser.screenshots import capture_page_screenshot
from app.web_tools.providers.duckduckgo_provider import DuckDuckGoSearchProvider


@dataclass(slots=True)
class WebAutomationAdapter:
    manager: PlaywrightManager = field(default_factory=get_shared_playwright_manager)
    search_provider: DuckDuckGoSearchProvider = field(default_factory=DuckDuckGoSearchProvider)

    def _get_active_session(self, *, bring_to_front: bool = False) -> tuple[str, PlaywrightSession]:
        return self.manager.get_active_persistent_session(bring_to_front=bring_to_front)

    @staticmethod
    def _flatten_browser_service_capture(result: dict[str, Any]) -> dict[str, Any]:
        data = result.get("data", {}) if isinstance(result.get("data", {}), dict) else {}
        merged = dict(data)
        for key in ("request_id", "action", "session_id", "url", "title", "ok", "error", "executed_via"):
            if key in result:
                merged[key] = result[key]
        return merged

    def web_open_url(self, *, url: str) -> dict[str, Any]:
        return call_browser_service("open_url", {"url": url})

    def web_get_title(self, *, url: str) -> dict[str, Any]:
        _session_id, session = self._get_active_session()
        open_url(session.page, url=url)
        return get_page_title(session.page)

    def web_extract_text(self, *, url: str) -> dict[str, Any]:
        _session_id, session = self._get_active_session()
        open_url(session.page, url=url)
        return get_page_text(session.page)

    def web_capture_page(self, *, url: str, full_page: bool = False) -> dict[str, Any]:
        return self._flatten_browser_service_capture(
            call_browser_service(
                "browser_screenshot",
                {"url": url, "full_page": bool(full_page), "name_prefix": "web_capture"},
            )
        )

    def web_save_page_html(self, *, url: str, name_prefix: str = "page") -> dict[str, Any]:
        _session_id, session = self._get_active_session()
        open_url(session.page, url=url)
        return save_page_html(session.page, name_prefix=name_prefix)

    def web_save_page_text(self, *, url: str, name_prefix: str = "page") -> dict[str, Any]:
        _session_id, session = self._get_active_session()
        open_url(session.page, url=url)
        return save_page_text(session.page, name_prefix=name_prefix)

    def web_search_duckduckgo(self, *, query: str) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        return self.search_provider.search(page=session.page, query=query)

    def web_click(self, *, url: str, selector: str, wait_after_ms: int = 0) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        open_url(session.page, url=url)
        result = click_locator(session.page, selector=selector)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
            result["wait_after_ms"] = int(wait_after_ms)
            result["url"] = session.page.url
            result["title"] = session.page.title()
        return result

    def web_type(self, *, url: str, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        open_url(session.page, url=url)
        return type_into_locator(session.page, selector=selector, text=text, clear_first=bool(clear_first))

    def web_press_key(self, *, url: str, key: str, wait_after_ms: int = 0) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        open_url(session.page, url=url)
        result = press_key(session.page, key=key)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
            result["wait_after_ms"] = int(wait_after_ms)
            result["url"] = session.page.url
            result["title"] = session.page.title()
        return result

    def web_open_and_capture(self, *, url: str, full_page: bool = False, wait_after_ms: int = 0) -> dict[str, Any]:
        if wait_after_ms > 0:
            time_result = call_browser_service("open_url", {"url": url})
            if not bool(time_result.get("ok", False)):
                return time_result
            import time
            time.sleep(max(0, int(wait_after_ms or 0)) / 1000)
            result = self._flatten_browser_service_capture(
                call_browser_service(
                    "browser_screenshot",
                    {"full_page": bool(full_page), "name_prefix": "web_open_capture"},
                )
            )
        else:
            result = self._flatten_browser_service_capture(
                call_browser_service(
                    "browser_screenshot",
                    {"url": url, "full_page": bool(full_page), "name_prefix": "web_open_capture"},
                )
            )
        result["wait_after_ms"] = max(0, int(wait_after_ms or 0))
        return result

    def web_type_and_press(
        self,
        *,
        url: str,
        selector: str,
        text: str,
        key: str = "Enter",
        clear_first: bool = True,
        wait_after_ms: int = 1000,
    ) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        open_url(session.page, url=url)
        type_result = type_into_locator(session.page, selector=selector, text=text, clear_first=bool(clear_first))
        press_result = press_key(session.page, key=key)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
        return {
            "ok": bool(type_result.get("ok")) and bool(press_result.get("ok")),
            "selector": str(selector or "").strip(),
            "typed_text": str(text or ""),
            "key": str(key or "").strip(),
            "clear_first": bool(clear_first),
            "wait_after_ms": max(0, int(wait_after_ms or 0)),
            "url": session.page.url,
            "title": session.page.title(),
        }

    def web_search_and_capture(self, *, query: str, full_page: bool = False, wait_after_ms: int = 1200) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        search_result = self.search_provider.search(page=session.page, query=query)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
        capture_result = capture_page_screenshot(session.page, name_prefix="web_search_capture", full_page=bool(full_page))
        return {
            "ok": bool(search_result.get("error", "") == "") and bool(capture_result.get("ok")),
            "provider": search_result.get("provider", "duckduckgo"),
            "query": str(query or "").strip(),
            "search_url": search_result.get("url", ""),
            "search_title": search_result.get("title", ""),
            "capture_path": capture_result.get("path", ""),
            "capture_filename": capture_result.get("filename", ""),
            "full_page": bool(full_page),
            "wait_after_ms": max(0, int(wait_after_ms or 0)),
            "url": session.page.url,
            "title": session.page.title(),
            "error": str(search_result.get("error") or ""),
        }

    def web_search_and_extract(self, *, query: str, wait_after_ms: int = 1200) -> dict[str, Any]:
        _session_id, session = self._get_active_session(bring_to_front=True)
        search_result = self.search_provider.search(page=session.page, query=query)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
        text_result = get_page_text(session.page)
        return {
            "ok": bool(search_result.get("error", "") == "") and bool(text_result.get("ok")),
            "provider": search_result.get("provider", "duckduckgo"),
            "query": str(query or "").strip(),
            "search_url": search_result.get("url", ""),
            "search_title": search_result.get("title", ""),
            "url": text_result.get("url", ""),
            "title": text_result.get("title", ""),
            "text": text_result.get("text", ""),
            "length": int(text_result.get("length", 0)),
            "line_count": int(text_result.get("line_count", 0)),
            "wait_after_ms": max(0, int(wait_after_ms or 0)),
            "error": str(search_result.get("error") or ""),
        }

    def web_session_start(self, *, url: str = "") -> dict[str, Any]:
        clean_url = str(url or "").strip()
        if clean_url:
            result = call_browser_service("open_url", {"url": clean_url})
            result["opened"] = result.get("data")
            return result
        return call_browser_service("open_browser")

    def web_session_stop(self, *, session_id: str) -> dict[str, Any]:
        closed = self.manager.close_persistent_session(session_id)
        return {
            "ok": bool(closed),
            "session_id": str(session_id or "").strip(),
            "closed": bool(closed),
            "error": "" if closed else "unknown_session",
        }

    def web_session_info(self, *, session_id: str) -> dict[str, Any]:
        result = call_browser_service("session_info")
        if session_id and result.get("session_id"):
            result["requested_session_id"] = str(session_id or "").strip()
        return result

    def web_session_open_url(self, *, session_id: str, url: str) -> dict[str, Any]:
        session = self._get_persistent_session(session_id)
        result = open_url(session.page, url=url)
        result["session_id"] = str(session_id or "").strip()
        return result

    def web_session_type(self, *, session_id: str, selector: str, text: str, clear_first: bool = True) -> dict[str, Any]:
        session = self._get_persistent_session(session_id)
        result = type_into_locator(session.page, selector=selector, text=text, clear_first=bool(clear_first))
        result["session_id"] = str(session_id or "").strip()
        return result

    def web_session_click(self, *, session_id: str, selector: str, wait_after_ms: int = 0) -> dict[str, Any]:
        session = self._get_persistent_session(session_id)
        result = click_locator(session.page, selector=selector)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
            result["wait_after_ms"] = int(wait_after_ms)
            result["url"] = session.page.url
            result["title"] = session.page.title()
        result["session_id"] = str(session_id or "").strip()
        return result

    def web_session_press_key(self, *, session_id: str, key: str, wait_after_ms: int = 0) -> dict[str, Any]:
        session = self._get_persistent_session(session_id)
        result = press_key(session.page, key=key)
        if wait_after_ms > 0:
            wait_ms(session.page, timeout_ms=wait_after_ms)
            result["wait_after_ms"] = int(wait_after_ms)
            result["url"] = session.page.url
            result["title"] = session.page.title()
        result["session_id"] = str(session_id or "").strip()
        return result

    def web_session_extract_text(self, *, session_id: str) -> dict[str, Any]:
        session = self._get_persistent_session(session_id)
        result = get_page_text(session.page)
        result["session_id"] = str(session_id or "").strip()
        return result

    def web_session_capture_page(self, *, session_id: str, full_page: bool = False) -> dict[str, Any]:
        result = self._flatten_browser_service_capture(
            call_browser_service(
                "browser_screenshot",
                {"full_page": bool(full_page), "name_prefix": "web_session_capture"},
            )
        )
        result["requested_session_id"] = str(session_id or "").strip()
        return result

    def web_session_list(self) -> dict[str, Any]:
        result = call_browser_service("session_info")
        session_ids = [str(result.get("session_id") or "").strip()] if result.get("ok") and result.get("session_id") else []
        return {
            "ok": True,
            "session_ids": session_ids,
            "count": len(session_ids),
        }

    def web_session_close_all(self) -> dict[str, Any]:
        closed_count = self.manager.close_all_persistent_sessions()
        return {
            "ok": True,
            "closed_count": int(closed_count),
        }
    

    
    def _get_persistent_session(self, session_id: str) -> PlaywrightSession:
        return self.manager.get_persistent_session(str(session_id or "").strip())
