from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("list_user_spaces")
    assert result.tool_name == "list_user_spaces"
    assert result.ok is True

    result = server.call_tool("get_recent_context")
    assert result.tool_name == "get_recent_context"
    assert result.ok is True

    result = server.call_tool("get_live_context")
    assert result.tool_name == "get_live_context"
    assert result.ok is True

    result = server.call_tool("get_user_profile_context")
    assert result.tool_name == "get_user_profile_context"
    assert result.ok is True

    result = server.call_tool("search_memory", query="rick", limit=3)
    assert result.tool_name == "search_memory"
    assert "query" in result.data

    print("test_memory_tools=ok")


if __name__ == "__main__":
    main()