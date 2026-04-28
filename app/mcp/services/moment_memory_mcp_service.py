from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.moment_memory_adapter import MomentMemoryAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class MomentMemoryMCPService:
    """
    MCP-facing service for moment_memory snapshots/status.

    Read-only in this phase.
    """

    adapter: MomentMemoryAdapter = field(default_factory=MomentMemoryAdapter)

    def read_context_snapshot(self) -> MCPToolResult:
        data = self.adapter.read_context_snapshot()
        return MCPToolResult(
            ok=True,
            tool_name="read_context_snapshot",
            message="Context snapshot loaded.",
            data=data,
        )

    def read_memory_snapshot(self) -> MCPToolResult:
        data = self.adapter.read_memory_snapshot()
        return MCPToolResult(
            ok=True,
            tool_name="read_memory_snapshot",
            message="Memory snapshot loaded.",
            data=data,
        )

    def read_world_state(self) -> MCPToolResult:
        data = self.adapter.read_world_state()
        return MCPToolResult(
            ok=True,
            tool_name="read_world_state",
            message="World state loaded.",
            data=data,
        )

    def read_context_runner_status(self) -> MCPToolResult:
        data = self.adapter.read_context_runner_status()
        return MCPToolResult(
            ok=True,
            tool_name="read_context_runner_status",
            message="Context runner status loaded.",
            data=data,
        )

    def read_context_runner_cursor(self) -> MCPToolResult:
        data = self.adapter.read_context_runner_cursor()
        return MCPToolResult(
            ok=True,
            tool_name="read_context_runner_cursor",
            message="Context runner cursor loaded.",
            data=data,
        )