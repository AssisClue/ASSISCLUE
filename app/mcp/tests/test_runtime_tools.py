from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("read_system_runtime_state")
    assert result.tool_name == "read_system_runtime_state"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = server.call_tool("read_llm_runtime_state")
    assert result.tool_name == "read_llm_runtime_state"
    assert isinstance(result.ok, bool)

    result = server.call_tool("read_recent_chat_history", limit=5)
    assert result.tool_name == "read_recent_chat_history"
    assert result.ok is True
    assert isinstance(result.data, dict)
    assert "items" in result.data

    result = server.call_tool("read_latest_response")
    assert result.tool_name == "read_latest_response"
    assert result.ok is True

    result = server.call_tool("read_latest_tts")
    assert result.tool_name == "read_latest_tts"
    assert result.ok is True

    result = server.call_tool("read_latest_decision")
    assert result.tool_name == "read_latest_decision"
    assert result.ok is True

    print("test_runtime_tools=ok")


if __name__ == "__main__":
    main()