from __future__ import annotations

from app.services.mcp_gateway_service import MCPGatewayService


def main() -> None:
    gateway = MCPGatewayService()

    result = gateway.read_system_runtime_state()
    assert result.tool_name == "read_system_runtime_state"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = gateway.read_context_snapshot()
    assert result.tool_name == "read_context_snapshot"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = gateway.read_text_file_safe(path="README.md")
    assert result.tool_name == "read_text_file_safe"
    assert result.ok is True
    assert isinstance(result.data, dict)

    result = gateway.search_memory(query="rick", limit=3)
    assert result.tool_name == "search_memory"
    assert isinstance(result.ok, bool)

    print("test_mcp_gateway_service=ok")


if __name__ == "__main__":
    main()