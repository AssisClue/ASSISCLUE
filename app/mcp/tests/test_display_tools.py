from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("capture_screenshot")
    assert result.tool_name == "capture_screenshot"
    assert isinstance(result.ok, bool)
    assert isinstance(result.data, dict)
    assert "screenshot_path" in result.data

    result = server.call_tool("analyze_latest_screenshot")
    assert result.tool_name == "analyze_latest_screenshot"
    assert isinstance(result.ok, bool)
    assert isinstance(result.data, dict)

    print("test_display_tools=ok")


if __name__ == "__main__":
    main()