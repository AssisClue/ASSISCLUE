from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.display_adapter import DisplayAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class DisplayMCPService:
    """
    MCP-facing display service.

    Responsibilities:
    - expose screenshot/display operations as normalized MCP results
    - keep MCP callers independent from display runner request shapes
    """

    adapter: DisplayAdapter = field(default_factory=DisplayAdapter)

    def capture_screenshot(self) -> MCPToolResult:
        data = self.adapter.capture_screenshot()
        return MCPToolResult(
            ok=bool(data.get("ok", False)),
            tool_name="capture_screenshot",
            message=str(data.get("speech_text") or "Screenshot capture finished."),
            data=data,
            error_code="" if bool(data.get("ok", False)) else str(data.get("error_code") or "capture_failed"),
        )

    def capture_full_screenshot(self) -> MCPToolResult:
        data = self.adapter.capture_full_screenshot()
        return MCPToolResult(
            ok=bool(data.get("ok", False)),
            tool_name="capture_full_screenshot",
            message=str(data.get("speech_text") or "Full screenshot capture finished."),
            data=data,
            error_code="" if bool(data.get("ok", False)) else str(data.get("error_code") or "capture_failed"),
        )

    def analyze_latest_screenshot(self) -> MCPToolResult:
        data = self.adapter.analyze_latest_screenshot()
        return MCPToolResult(
            ok=bool(data.get("ok", False)),
            tool_name="analyze_latest_screenshot",
            message=str(data.get("speech_text") or "Latest screenshot analysis finished."),
            data=data,
            error_code="" if bool(data.get("ok", False)) else str(data.get("error_code") or "analysis_failed"),
        )

    def analyze_current_screen(self) -> MCPToolResult:
        data = self.adapter.analyze_current_screen()
        return MCPToolResult(
            ok=bool(data.get("ok", False)),
            tool_name="analyze_current_screen",
            message=str(data.get("speech_text") or "Current screen analysis finished."),
            data=data,
            error_code="" if bool(data.get("ok", False)) else str(data.get("error_code") or "analysis_failed"),
        )