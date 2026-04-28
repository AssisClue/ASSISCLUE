from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.mcp.schemas import MCPToolResult
from app.services.mcp_gateway_runtime import get_mcp_server


@dataclass(slots=True)
class MCPGatewayService:
    """
    App-facing gateway for MCP access.

    The rest of the app should prefer calling this service instead of importing
    app.mcp.server directly.
    """

    def _call(self, tool_name: str, **kwargs: Any) -> MCPToolResult:
        server = get_mcp_server()
        result = server.call_tool(tool_name, **kwargs)
        if not isinstance(result, MCPToolResult):
            return MCPToolResult(
                ok=False,
                tool_name=tool_name,
                message="Tool returned unexpected result type.",
                error_code="invalid_tool_result",
                data={"tool_name": tool_name, "kwargs": kwargs},
                meta={"result_type": type(result).__name__},
            )
        return result

    # -------- memory --------

    def search_memory(
        self,
        *,
        query: str,
        limit: int = 5,
        preferred_sources: list[str] | None = None,
    ) -> MCPToolResult:
        return self._call(
            "search_memory",
            query=query,
            limit=limit,
            preferred_sources=list(preferred_sources or []),
        )

    def get_recent_context(self) -> MCPToolResult:
        return self._call("get_recent_context")

    def get_live_context(self) -> MCPToolResult:
        return self._call("get_live_context")

    def get_user_profile_context(self) -> MCPToolResult:
        return self._call("get_user_profile_context")

    def get_task_context(
        self,
        *,
        task_type: str,
        query: str = "",
        project_name: str = "",
        preferred_sources: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> MCPToolResult:
        return self._call(
            "get_task_context",
            task_type=task_type,
            query=query,
            project_name=project_name,
            preferred_sources=list(preferred_sources or []),
            tags=list(tags or []),
        )

    def list_user_spaces(self) -> MCPToolResult:
        return self._call("list_user_spaces")

    def get_user_space(
        self,
        *,
        space_id: str,
        query: str = "",
        limit: int = 20,
    ) -> MCPToolResult:
        return self._call(
            "get_user_space",
            space_id=space_id,
            query=query,
            limit=limit,
        )

    # -------- runtime --------

    def read_system_runtime_state(self) -> MCPToolResult:
        return self._call("read_system_runtime_state")

    def read_llm_runtime_state(self) -> MCPToolResult:
        return self._call("read_llm_runtime_state")

    def read_recent_chat_history(self, *, limit: int = 20) -> MCPToolResult:
        return self._call("read_recent_chat_history", limit=limit)

    def read_latest_response(self) -> MCPToolResult:
        return self._call("read_latest_response")

    def read_latest_tts(self) -> MCPToolResult:
        return self._call("read_latest_tts")

    def read_latest_decision(self) -> MCPToolResult:
        return self._call("read_latest_decision")

    # -------- display --------

    def capture_screenshot(self) -> MCPToolResult:
        return self._call("capture_screenshot")

    def capture_full_screenshot(self) -> MCPToolResult:
        return self._call("capture_full_screenshot")

    def analyze_latest_screenshot(self) -> MCPToolResult:
        return self._call("analyze_latest_screenshot")

    def analyze_current_screen(self) -> MCPToolResult:
        return self._call("analyze_current_screen")

    # -------- webautomation --------

    def web_session_list(self) -> MCPToolResult:
        return self._call("web_session_list")

    def web_session_start(self, *, url: str = "") -> MCPToolResult:
        return self._call("web_session_start", url=url)

    def web_session_info(self, *, session_id: str) -> MCPToolResult:
        return self._call("web_session_info", session_id=session_id)

    def web_session_open_url(self, *, session_id: str, url: str) -> MCPToolResult:
        return self._call("web_session_open_url", session_id=session_id, url=url)

    def web_session_type(
        self,
        *,
        session_id: str,
        selector: str,
        text: str,
        clear_first: bool = True,
    ) -> MCPToolResult:
        return self._call(
            "web_session_type",
            session_id=session_id,
            selector=selector,
            text=text,
            clear_first=clear_first,
        )

    def web_session_press_key(
        self,
        *,
        session_id: str,
        key: str,
        wait_after_ms: int = 0,
    ) -> MCPToolResult:
        return self._call(
            "web_session_press_key",
            session_id=session_id,
            key=key,
            wait_after_ms=wait_after_ms,
        )

    def web_session_capture_page(
        self,
        *,
        session_id: str,
        full_page: bool = True,
    ) -> MCPToolResult:
        return self._call(
            "web_session_capture_page",
            session_id=session_id,
            full_page=full_page,
        )

    def web_session_stop(self, *, session_id: str) -> MCPToolResult:
        return self._call("web_session_stop", session_id=session_id)

    def web_session_stop_all(self) -> MCPToolResult:
        return self._call("web_session_stop_all")

    # -------- workspace --------

    def read_text_file(self, *, path: str) -> MCPToolResult:
        return self._call("read_text_file", path=path)

    def read_text_file_safe(self, *, path: str) -> MCPToolResult:
        return self._call("read_text_file_safe", path=path)

    def read_python_file(self, *, path: str) -> MCPToolResult:
        return self._call("read_python_file", path=path)

    def read_json_file(self, *, path: str) -> MCPToolResult:
        return self._call("read_json_file", path=path)

    def append_note(self, *, path: str, text: str) -> MCPToolResult:
        return self._call("append_note", path=path, text=text)

    def overwrite_note(self, *, path: str, text: str) -> MCPToolResult:
        return self._call("overwrite_note", path=path, text=text)

    # -------- moment_memory --------

    def read_context_snapshot(self) -> MCPToolResult:
        return self._call("read_context_snapshot")

    def read_memory_snapshot(self) -> MCPToolResult:
        return self._call("read_memory_snapshot")

    def read_world_state(self) -> MCPToolResult:
        return self._call("read_world_state")

    def read_context_runner_status(self) -> MCPToolResult:
        return self._call("read_context_runner_status")

    def read_context_runner_cursor(self) -> MCPToolResult:
        return self._call("read_context_runner_cursor")

    # -------- personas --------

    def list_personas(self) -> MCPToolResult:
        return self._call("list_personas")

    def get_persona(self, *, persona_id: str) -> MCPToolResult:
        return self._call("get_persona", persona_id=persona_id)

    def get_active_persona_id(self) -> MCPToolResult:
        return self._call("get_active_persona_id")