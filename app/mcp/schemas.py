from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MCPToolResult:
    """
    Generic normalized result shape for MCP-facing tool responses.

    This is intentionally small and generic for phase 1.
    More specific schemas can be added later per domain.
    """

    ok: bool = True
    tool_name: str = ""
    message: str = ""
    data: Any = None
    error_code: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class MCPToolDefinition:
    """
    Lightweight internal description of a registered MCP tool.

    Phase 1 keeps this minimal and framework-agnostic.
    """

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MCPServerInfo:
    """
    Basic metadata for the local MCP block.
    """

    name: str = "assistant-core-mcp"
    version: str = "0.1.0"
    description: str = "MCP facade for the local assistant app"


@dataclass(slots=True)
class MCPRegistrySnapshot:
    """
    Simple export shape used to inspect the current registered tools.
    """

    server_name: str
    total_tools: int
    tools: list[MCPToolDefinition] = field(default_factory=list)