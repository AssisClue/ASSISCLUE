from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("search_web", query="python")
    assert result.tool_name == "search_web"
    assert isinstance(result.ok, bool)
    assert isinstance(result.data, dict)
    assert "query" in result.data
    assert "results" in result.data

    print("test_websearch_tools=ok")


if __name__ == "__main__":
    main()