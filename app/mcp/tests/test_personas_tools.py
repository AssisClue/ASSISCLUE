from __future__ import annotations

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()

    result = server.call_tool("list_personas")
    assert result.tool_name == "list_personas"
    assert result.ok is True
    assert isinstance(result.data, dict)
    assert "items" in result.data

    items = result.data.get("items", [])
    assert isinstance(items, list)

    if items:
        first = items[0]
        persona_id = str(first.get("persona_id") or "").strip()
        if persona_id:
            lookup = server.call_tool("get_persona", persona_id=persona_id)
            assert lookup.tool_name == "get_persona"
            assert lookup.ok is True
            assert isinstance(lookup.data, dict)
            assert lookup.data.get("found") is True

    active = server.call_tool("get_active_persona_id")
    assert active.tool_name == "get_active_persona_id"
    assert active.ok is True
    assert isinstance(active.data, dict)

    print("test_personas_tools=ok")


if __name__ == "__main__":
    main()