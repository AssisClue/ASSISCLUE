from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.mcp.registry import MCPToolRegistry, create_registry, register_all_tools

from app.mcp.schemas import MCPRegistrySnapshot, MCPServerInfo


@dataclass(slots=True)
class MCPServer:
    """
    Local MCP server skeleton.

    Phase 1 purpose:
    - hold MCP metadata
    - own the registry
    - provide a clean place for future MCP SDK wiring

    This is intentionally framework-agnostic for now.
    """

    info: MCPServerInfo = field(default_factory=MCPServerInfo)
    registry: MCPToolRegistry = field(default_factory=create_registry)

    def get_info(self) -> MCPServerInfo:
        return self.info

    def get_registry_snapshot(self) -> MCPRegistrySnapshot:
        return self.registry.export_snapshot(server_name=self.info.name)

    def register_tool(
        self,
        *,
        name: str,
        description: str,
        handler,
        input_schema: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        self.registry.register(
            name=name,
            description=description,
            handler=handler,
            input_schema=input_schema,
            tags=tags,
        )

    def call_tool(self, name: str, **kwargs: Any) -> object:
        handler = self.registry.get_handler(name)
        return handler(**kwargs)


def create_mcp_server() -> MCPServer:
    """
    Create the MCP server and register the current phase tools.
    """
    server = MCPServer()
    register_all_tools(server)
    return server



def main() -> None:
    """
    Minimal local debug entrypoint for early verification.
    """
    server = create_mcp_server()
    snapshot = server.get_registry_snapshot()

    print(f"MCP server: {server.get_info().name}")
    print(f"Version: {server.get_info().version}")
    print(f"Registered tools: {snapshot.total_tools}")


if __name__ == "__main__":
    main()