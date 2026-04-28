from __future__ import annotations

from app.mcp.services.moment_memory_mcp_service import MomentMemoryMCPService


def register_moment_memory_tools(server) -> None:
    service = MomentMemoryMCPService()

    server.register_tool(
        name="read_context_snapshot",
        description="Read runtime sacred context snapshot produced by moment_memory.",
        handler=service.read_context_snapshot,
        input_schema={"type": "object", "properties": {}},
        tags=["moment_memory", "snapshot", "read"],
    )

    server.register_tool(
        name="read_memory_snapshot",
        description="Read runtime sacred memory snapshot produced by moment_memory.",
        handler=service.read_memory_snapshot,
        input_schema={"type": "object", "properties": {}},
        tags=["moment_memory", "snapshot", "read"],
    )

    server.register_tool(
        name="read_world_state",
        description="Read runtime sacred world state produced by moment_memory.",
        handler=service.read_world_state,
        input_schema={"type": "object", "properties": {}},
        tags=["moment_memory", "world_state", "read"],
    )

    server.register_tool(
        name="read_context_runner_status",
        description="Read context_runner status payload.",
        handler=service.read_context_runner_status,
        input_schema={"type": "object", "properties": {}},
        tags=["moment_memory", "status", "read"],
    )

    server.register_tool(
        name="read_context_runner_cursor",
        description="Read context_runner cursor payload.",
        handler=service.read_context_runner_cursor,
        input_schema={"type": "object", "properties": {}},
        tags=["moment_memory", "cursor", "read"],
    )