from __future__ import annotations

from dataclasses import dataclass, field

from sympy import limit

from app.mcp.adapters.router_dispatch_adapter import RouterDispatchAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class RouterDispatchMCPService:
    """
    MCP-facing service for read-only router_dispatch inspection.
    """

    adapter: RouterDispatchAdapter = field(default_factory=RouterDispatchAdapter)

    def read_router_dispatch_status(self) -> MCPToolResult:
        data = self.adapter.read_router_dispatch_status()
        return MCPToolResult(
            ok=True,
            tool_name="read_router_dispatch_status",
            message="Router dispatch status loaded.",
            data=data,
        )

    def tail_router_dispatch_queue(
        self,
        *,
        queue: str,
        limit: int = 50,
    ) -> MCPToolResult:
        clean_queue = str(queue or "").strip().lower()

        clean_limit = min(200, max(1, int(limit or 50)))

        data = self.adapter.tail_router_dispatch_queue(
            queue=clean_queue,
            limit=clean_limit,
        )

        if data.get("error") == "invalid_queue":
            return MCPToolResult(
                ok=False,
                tool_name="tail_router_dispatch_queue",
                message="Queue must be router_input, action, or response.",
                error_code="invalid_queue",
                data=data,
            )

        return MCPToolResult(
            ok=True,
            tool_name="tail_router_dispatch_queue",
            message="Router dispatch queue tail loaded.",
            data=data,
            meta={"queue": clean_queue, "limit": clean_limit},
        )
