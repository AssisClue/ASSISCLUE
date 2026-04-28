from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("list_capabilities")
    assert result.tool_name == "list_capabilities"
    assert result.ok is True
    assert isinstance(result.data, dict)
    assert "items" in result.data

    items = result.data.get("items", [])
    assert isinstance(items, list)

    if items:
        first = items[0]
        action_name = str(first.get("action_name") or "").strip()
        if action_name:
            lookup = server.call_tool("get_capability_by_action_name", action_name=action_name)
            assert lookup.tool_name == "get_capability_by_action_name"
            assert lookup.ok is True
            assert isinstance(lookup.data, dict)
            assert lookup.data.get("found") is True

    print("test_capabilities_tools=ok")


if __name__ == "__main__":
    main()