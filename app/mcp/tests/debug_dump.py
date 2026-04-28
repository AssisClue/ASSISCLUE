from __future__ import annotations

from pprint import pprint

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()
    snapshot = server.get_registry_snapshot()

    print("=== MCP INFO ===")
    print(server.get_info())

    print("\n=== REGISTERED TOOLS ===")
    for tool in snapshot.tools:
        print(f"- {tool.name} | tags={tool.tags}")

    print("\n=== SAMPLE CALL: read_system_runtime_state ===")
    pprint(server.call_tool("read_system_runtime_state"))

    print("\n=== SAMPLE CALL: read_text_file_safe(README.md) ===")
    pprint(server.call_tool("read_text_file_safe", path="README.md"))


if __name__ == "__main__":
    main()