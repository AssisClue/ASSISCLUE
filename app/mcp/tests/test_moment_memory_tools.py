from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("read_context_snapshot")
    assert result.tool_name == "read_context_snapshot"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = server.call_tool("read_memory_snapshot")
    assert result.tool_name == "read_memory_snapshot"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = server.call_tool("read_world_state")
    assert result.tool_name == "read_world_state"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = server.call_tool("read_context_runner_status")
    assert result.tool_name == "read_context_runner_status"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = server.call_tool("read_context_runner_cursor")
    assert result.tool_name == "read_context_runner_cursor"
    assert result.ok is True
    assert isinstance(result.data, dict)

    print("test_moment_memory_tools=ok")


if __name__ == "__main__":
    main()