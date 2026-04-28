from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.schemas import MCPToolResult
from app.mcp.webautomation.adapters.webautomation_adapter import WebAutomationAdapter


@dataclass(slots=True)
class WebAutomationMCPService:
    """
    MCP-facing service for Playwright-backed web automation.
    """

    adapter: WebAutomationAdapter = field(default_factory=WebAutomationAdapter)

    def web_open_url(self, *, url: str) -> MCPToolResult:
        clean_url = str(url or "").strip()
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_open_url", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url})
        try:
            data = self.adapter.web_open_url(url=clean_url)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_open_url", message="Web page opened.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_open_url", message="Failed to open URL.", error_code="web_open_url_error", data={"url": clean_url}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_get_title(self, *, url: str) -> MCPToolResult:
        clean_url = str(url or "").strip()
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_get_title", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url})
        try:
            data = self.adapter.web_get_title(url=clean_url)
            return MCPToolResult(ok=True, tool_name="web_get_title", message="Page title loaded.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_get_title", message="Failed to load page title.", error_code="web_get_title_error", data={"url": clean_url}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_extract_text(self, *, url: str) -> MCPToolResult:
        clean_url = str(url or "").strip()
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_extract_text", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url})
        try:
            data = self.adapter.web_extract_text(url=clean_url)
            return MCPToolResult(ok=True, tool_name="web_extract_text", message="Page text extracted.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_extract_text", message="Failed to extract page text.", error_code="web_extract_text_error", data={"url": clean_url}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_capture_page(self, *, url: str, full_page: bool = False) -> MCPToolResult:
        clean_url = str(url or "").strip()
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_capture_page", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url})
        try:
            data = self.adapter.web_capture_page(url=clean_url, full_page=bool(full_page))
            return MCPToolResult(ok=True, tool_name="web_capture_page", message="Page screenshot captured.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_capture_page", message="Failed to capture page screenshot.", error_code="web_capture_page_error", data={"url": clean_url, "full_page": bool(full_page)}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_save_page_html(self, *, url: str, name_prefix: str = "page") -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_name_prefix = str(name_prefix or "").strip() or "page"
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_save_page_html", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "name_prefix": clean_name_prefix})
        try:
            data = self.adapter.web_save_page_html(url=clean_url, name_prefix=clean_name_prefix)
            return MCPToolResult(ok=True, tool_name="web_save_page_html", message="Page HTML saved.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_save_page_html", message="Failed to save page HTML.", error_code="web_save_page_html_error", data={"url": clean_url, "name_prefix": clean_name_prefix}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_save_page_text(self, *, url: str, name_prefix: str = "page") -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_name_prefix = str(name_prefix or "").strip() or "page"
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_save_page_text", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "name_prefix": clean_name_prefix})
        try:
            data = self.adapter.web_save_page_text(url=clean_url, name_prefix=clean_name_prefix)
            return MCPToolResult(ok=True, tool_name="web_save_page_text", message="Page text saved.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_save_page_text", message="Failed to save page text.", error_code="web_save_page_text_error", data={"url": clean_url, "name_prefix": clean_name_prefix}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_search_duckduckgo(self, *, query: str) -> MCPToolResult:
        clean_query = str(query or "").strip()
        if not clean_query:
            return MCPToolResult(ok=False, tool_name="web_search_duckduckgo", message="Query cannot be empty.", error_code="empty_query", data={"query": clean_query})
        try:
            data = self.adapter.web_search_duckduckgo(query=clean_query)
            return MCPToolResult(ok=not bool(data.get("error")), tool_name="web_search_duckduckgo", message="DuckDuckGo search completed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_search_duckduckgo", message="DuckDuckGo search failed.", error_code="web_search_duckduckgo_error", data={"query": clean_query}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_click(self, *, url: str, selector: str, wait_after_ms: int = 0) -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_selector = str(selector or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_click", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "selector": clean_selector})
        if not clean_selector:
            return MCPToolResult(ok=False, tool_name="web_click", message="Selector cannot be empty.", error_code="empty_selector", data={"url": clean_url, "selector": clean_selector})
        try:
            data = self.adapter.web_click(url=clean_url, selector=clean_selector, wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_click", message="Web click executed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_click", message="Web click failed.", error_code="web_click_error", data={"url": clean_url, "selector": clean_selector, "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_type(self, *, url: str, selector: str, text: str, clear_first: bool = True) -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_selector = str(selector or "").strip()
        clean_text = str(text or "")
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_type", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "selector": clean_selector, "text": clean_text})
        if not clean_selector:
            return MCPToolResult(ok=False, tool_name="web_type", message="Selector cannot be empty.", error_code="empty_selector", data={"url": clean_url, "selector": clean_selector, "text": clean_text})
        try:
            data = self.adapter.web_type(url=clean_url, selector=clean_selector, text=clean_text, clear_first=bool(clear_first))
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_type", message="Web type executed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_type", message="Web type failed.", error_code="web_type_error", data={"url": clean_url, "selector": clean_selector, "text": clean_text, "clear_first": bool(clear_first)}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_press_key(self, *, url: str, key: str, wait_after_ms: int = 0) -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_key = str(key or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_press_key", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "key": clean_key})
        if not clean_key:
            return MCPToolResult(ok=False, tool_name="web_press_key", message="Key cannot be empty.", error_code="empty_key", data={"url": clean_url, "key": clean_key})
        try:
            data = self.adapter.web_press_key(url=clean_url, key=clean_key, wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_press_key", message="Web key press executed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_press_key", message="Web key press failed.", error_code="web_press_key_error", data={"url": clean_url, "key": clean_key, "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_open_and_capture(self, *, url: str, full_page: bool = False, wait_after_ms: int = 0) -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_open_and_capture", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "full_page": bool(full_page), "wait_after_ms": clean_wait_after_ms})
        try:
            data = self.adapter.web_open_and_capture(url=clean_url, full_page=bool(full_page), wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_open_and_capture", message="Web open and capture completed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_open_and_capture", message="Web open and capture failed.", error_code="web_open_and_capture_error", data={"url": clean_url, "full_page": bool(full_page), "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_type_and_press(self, *, url: str, selector: str, text: str, key: str = "Enter", clear_first: bool = True, wait_after_ms: int = 1000) -> MCPToolResult:
        clean_url = str(url or "").strip()
        clean_selector = str(selector or "").strip()
        clean_text = str(text or "")
        clean_key = str(key or "").strip() or "Enter"
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_type_and_press", message="URL cannot be empty.", error_code="empty_url", data={"url": clean_url, "selector": clean_selector, "text": clean_text})
        if not clean_selector:
            return MCPToolResult(ok=False, tool_name="web_type_and_press", message="Selector cannot be empty.", error_code="empty_selector", data={"url": clean_url, "selector": clean_selector, "text": clean_text})
        try:
            data = self.adapter.web_type_and_press(url=clean_url, selector=clean_selector, text=clean_text, key=clean_key, clear_first=bool(clear_first), wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_type_and_press", message="Web type and press executed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_type_and_press", message="Web type and press failed.", error_code="web_type_and_press_error", data={"url": clean_url, "selector": clean_selector, "text": clean_text, "key": clean_key, "clear_first": bool(clear_first), "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_search_and_capture(self, *, query: str, full_page: bool = False, wait_after_ms: int = 1200) -> MCPToolResult:
        clean_query = str(query or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_query:
            return MCPToolResult(ok=False, tool_name="web_search_and_capture", message="Query cannot be empty.", error_code="empty_query", data={"query": clean_query, "full_page": bool(full_page), "wait_after_ms": clean_wait_after_ms})
        try:
            data = self.adapter.web_search_and_capture(query=clean_query, full_page=bool(full_page), wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_search_and_capture", message="Web search and capture completed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_search_and_capture", message="Web search and capture failed.", error_code="web_search_and_capture_error", data={"query": clean_query, "full_page": bool(full_page), "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_search_and_extract(self, *, query: str, wait_after_ms: int = 1200) -> MCPToolResult:
        clean_query = str(query or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_query:
            return MCPToolResult(ok=False, tool_name="web_search_and_extract", message="Query cannot be empty.", error_code="empty_query", data={"query": clean_query, "wait_after_ms": clean_wait_after_ms})
        try:
            data = self.adapter.web_search_and_extract(query=clean_query, wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_search_and_extract", message="Web search and extract completed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_search_and_extract", message="Web search and extract failed.", error_code="web_search_and_extract_error", data={"query": clean_query, "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_start(self, *, url: str = "") -> MCPToolResult:
        clean_url = str(url or "").strip()
        try:
            data = self.adapter.web_session_start(url=clean_url)
            return MCPToolResult(ok=True, tool_name="web_session_start", message="Web session started.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_start", message="Failed to start web session.", error_code="web_session_start_error", data={"url": clean_url}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_stop(self, *, session_id: str) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_stop", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id})
        try:
            data = self.adapter.web_session_stop(session_id=clean_session_id)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_session_stop", message="Web session stop executed.", data=data, error_code=str(data.get("error") or ""))
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_stop", message="Failed to stop web session.", error_code="web_session_stop_error", data={"session_id": clean_session_id}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_info(self, *, session_id: str) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_info", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id})
        try:
            data = self.adapter.web_session_info(session_id=clean_session_id)
            return MCPToolResult(ok=True, tool_name="web_session_info", message="Web session info loaded.", data=data)
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_info", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_info", message="Failed to load web session info.", error_code="web_session_info_error", data={"session_id": clean_session_id}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_open_url(self, *, session_id: str, url: str) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        clean_url = str(url or "").strip()
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_open_url", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id, "url": clean_url})
        if not clean_url:
            return MCPToolResult(ok=False, tool_name="web_session_open_url", message="URL cannot be empty.", error_code="empty_url", data={"session_id": clean_session_id, "url": clean_url})
        try:
            data = self.adapter.web_session_open_url(session_id=clean_session_id, url=clean_url)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_session_open_url", message="Web session URL opened.", data=data, error_code=str(data.get("error") or ""))
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_open_url", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id, "url": clean_url})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_open_url", message="Failed to open URL in web session.", error_code="web_session_open_url_error", data={"session_id": clean_session_id, "url": clean_url}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_type(self, *, session_id: str, selector: str, text: str, clear_first: bool = True) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        clean_selector = str(selector or "").strip()
        clean_text = str(text or "")
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_type", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id, "selector": clean_selector, "text": clean_text})
        if not clean_selector:
            return MCPToolResult(ok=False, tool_name="web_session_type", message="Selector cannot be empty.", error_code="empty_selector", data={"session_id": clean_session_id, "selector": clean_selector, "text": clean_text})
        try:
            data = self.adapter.web_session_type(session_id=clean_session_id, selector=clean_selector, text=clean_text, clear_first=bool(clear_first))
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_session_type", message="Web session type executed.", data=data, error_code=str(data.get("error") or ""))
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_type", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id, "selector": clean_selector})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_type", message="Failed to type in web session.", error_code="web_session_type_error", data={"session_id": clean_session_id, "selector": clean_selector, "text": clean_text, "clear_first": bool(clear_first)}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_click(self, *, session_id: str, selector: str, wait_after_ms: int = 0) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        clean_selector = str(selector or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_click", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id, "selector": clean_selector})
        if not clean_selector:
            return MCPToolResult(ok=False, tool_name="web_session_click", message="Selector cannot be empty.", error_code="empty_selector", data={"session_id": clean_session_id, "selector": clean_selector})
        try:
            data = self.adapter.web_session_click(session_id=clean_session_id, selector=clean_selector, wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_session_click", message="Web session click executed.", data=data, error_code=str(data.get("error") or ""))
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_click", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id, "selector": clean_selector})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_click", message="Failed to click in web session.", error_code="web_session_click_error", data={"session_id": clean_session_id, "selector": clean_selector, "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_press_key(self, *, session_id: str, key: str, wait_after_ms: int = 0) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        clean_key = str(key or "").strip()
        clean_wait_after_ms = max(0, int(wait_after_ms or 0))
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_press_key", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id, "key": clean_key})
        if not clean_key:
            return MCPToolResult(ok=False, tool_name="web_session_press_key", message="Key cannot be empty.", error_code="empty_key", data={"session_id": clean_session_id, "key": clean_key})
        try:
            data = self.adapter.web_session_press_key(session_id=clean_session_id, key=clean_key, wait_after_ms=clean_wait_after_ms)
            return MCPToolResult(ok=bool(data.get("ok", True)), tool_name="web_session_press_key", message="Web session key press executed.", data=data, error_code=str(data.get("error") or ""))
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_press_key", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id, "key": clean_key})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_press_key", message="Failed to press key in web session.", error_code="web_session_press_key_error", data={"session_id": clean_session_id, "key": clean_key, "wait_after_ms": clean_wait_after_ms}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_extract_text(self, *, session_id: str) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_extract_text", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id})
        try:
            data = self.adapter.web_session_extract_text(session_id=clean_session_id)
            return MCPToolResult(ok=True, tool_name="web_session_extract_text", message="Web session text extracted.", data=data)
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_extract_text", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_extract_text", message="Failed to extract text from web session.", error_code="web_session_extract_text_error", data={"session_id": clean_session_id}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_capture_page(self, *, session_id: str, full_page: bool = False) -> MCPToolResult:
        clean_session_id = str(session_id or "").strip()
        if not clean_session_id:
            return MCPToolResult(ok=False, tool_name="web_session_capture_page", message="Session ID cannot be empty.", error_code="empty_session_id", data={"session_id": clean_session_id, "full_page": bool(full_page)})
        try:
            data = self.adapter.web_session_capture_page(session_id=clean_session_id, full_page=bool(full_page))
            return MCPToolResult(ok=True, tool_name="web_session_capture_page", message="Web session page captured.", data=data)
        except KeyError:
            return MCPToolResult(ok=False, tool_name="web_session_capture_page", message="Unknown web session.", error_code="unknown_session", data={"session_id": clean_session_id, "full_page": bool(full_page)})
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_capture_page", message="Failed to capture page from web session.", error_code="web_session_capture_page_error", data={"session_id": clean_session_id, "full_page": bool(full_page)}, meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_list(self) -> MCPToolResult:
        try:
            data = self.adapter.web_session_list()
            return MCPToolResult(ok=True, tool_name="web_session_list", message="Web session list loaded.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_list", message="Failed to load web session list.", error_code="web_session_list_error", meta={"exception": f"{type(exc).__name__}: {exc}"})

    def web_session_stop_all(self) -> MCPToolResult:
        try:
            data = self.adapter.web_session_close_all()
            return MCPToolResult(ok=True, tool_name="web_session_stop_all", message="All web sessions closed.", data=data)
        except Exception as exc:
            return MCPToolResult(ok=False, tool_name="web_session_stop_all", message="Failed to close all web sessions.", error_code="web_session_stop_all_error", meta={"exception": f"{type(exc).__name__}: {exc}"})