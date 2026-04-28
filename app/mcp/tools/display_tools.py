from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.mcp.server import MCPServer
    
from app.mcp.services.display_mcp_service import DisplayMCPService


def register_display_tools(server) -> None:
    service = DisplayMCPService()

    server.register_tool(
        name="capture_screenshot",
        description="Capture a standard screenshot.",
        handler=service.capture_screenshot,
        input_schema={"type": "object", "properties": {}},
        tags=["display", "screenshot", "write"],
    )

    server.register_tool(
        name="capture_full_screenshot",
        description="Capture a full screenshot.",
        handler=service.capture_full_screenshot,
        input_schema={"type": "object", "properties": {}},
        tags=["display", "screenshot", "write"],
    )

    server.register_tool(
        name="analyze_latest_screenshot",
        description="Analyze the latest available screenshot.",
        handler=service.analyze_latest_screenshot,
        input_schema={"type": "object", "properties": {}},
        tags=["display", "vision"],
    )

    server.register_tool(
        name="analyze_current_screen",
        description="Capture or reuse a screenshot and analyze the current screen.",
        handler=service.analyze_current_screen,
        input_schema={"type": "object", "properties": {}},
        tags=["display", "vision"],
    )