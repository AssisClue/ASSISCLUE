from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.capabilities_adapter import CapabilitiesAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class CapabilitiesMCPService:
    """
    MCP-facing service for capabilities.
    """

    adapter: CapabilitiesAdapter = field(default_factory=CapabilitiesAdapter)

    def list_capabilities(self) -> MCPToolResult:
        data = self.adapter.list_capabilities()
        return MCPToolResult(
            ok=True,
            tool_name="list_capabilities",
            message="Capabilities loaded.",
            data=data,
        )

    def get_capability_by_action_name(self, *, action_name: str) -> MCPToolResult:
        clean_action_name = str(action_name or "").strip()
        if not clean_action_name:
            return MCPToolResult(
                ok=False,
                tool_name="get_capability_by_action_name",
                message="Action name cannot be empty.",
                error_code="empty_action_name",
                data={"action_name": clean_action_name},
            )

        data = self.adapter.get_capability_by_action_name(action_name=clean_action_name)
        return MCPToolResult(
            ok=True,
            tool_name="get_capability_by_action_name",
            message="Capability lookup completed.",
            data=data,
        )