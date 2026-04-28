from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from app.mcp.schemas import MCPRegistrySnapshot, MCPToolDefinition


from app.mcp.tools.display_tools import register_display_tools
from app.mcp.tools.memory_tools import register_memory_tools
from app.mcp.tools.runtime_tools import register_runtime_tools
from app.mcp.tools.workspace_tools import register_workspace_tools
from app.mcp.tools.capabilities_tools import register_capabilities_tools
from app.mcp.webautomation.tools.webautomation_tools import register_webautomation_tools


from app.mcp.tools.personas_tools import register_personas_tools

from app.mcp.tools.moment_memory_tools import register_moment_memory_tools




def register_all_tools(server) -> None:
    register_memory_tools(server)
    register_runtime_tools(server)
    register_display_tools(server)
    register_workspace_tools(server)
    register_moment_memory_tools(server)
    register_capabilities_tools(server)
    register_personas_tools(server)        
    register_webautomation_tools(server)

@dataclass(slots=True)
class MCPToolEntry:
    """
    Internal registry entry.

    Keeps both the public definition and the callable handler.
    """

    definition: MCPToolDefinition
    handler: Callable[..., object]


@dataclass(slots=True)
class MCPToolRegistry:
    """
    Framework-agnostic in-process tool registry.

    Phase 1 uses this as the single source of truth for which tools
    exist in the MCP block, even before wiring to a specific MCP SDK.
    """

    _entries: dict[str, MCPToolEntry] = field(default_factory=dict)

    def register(
        self,
        *,
        name: str,
        description: str,
        handler: Callable[..., object],
        input_schema: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        clean_name = str(name).strip()
        if not clean_name:
            raise ValueError("Tool name cannot be empty.")

        if clean_name in self._entries:
            raise ValueError(f"Tool already registered: {clean_name}")

        definition = MCPToolDefinition(
            name=clean_name,
            description=str(description).strip(),
            input_schema=dict(input_schema or {}),
            tags=list(tags or []),
        )
        self._entries[clean_name] = MCPToolEntry(definition=definition, handler=handler)

    def has_tool(self, name: str) -> bool:
        return str(name).strip() in self._entries

    def get_handler(self, name: str) -> Callable[..., object]:
        clean_name = str(name).strip()
        entry = self._entries.get(clean_name)
        if entry is None:
            raise KeyError(f"Unknown tool: {clean_name}")
        return entry.handler

    def get_definitions(self) -> list[MCPToolDefinition]:
        return [entry.definition for entry in self._entries.values()]

    def export_snapshot(self, server_name: str) -> MCPRegistrySnapshot:
        definitions = self.get_definitions()
        return MCPRegistrySnapshot(
            server_name=server_name,
            total_tools=len(definitions),
            tools=definitions,
        )


def create_registry() -> MCPToolRegistry:
    """
    Factory kept explicit so future bootstrapping stays clean.
    """
    return MCPToolRegistry()