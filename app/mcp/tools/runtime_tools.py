from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.mcp.server import MCPServer

from app.mcp.services.router_dispatch_mcp_service import RouterDispatchMCPService
from app.mcp.services.runtime_mcp_service import RuntimeMCPService


def register_runtime_tools(server: MCPServer) -> None:
    service = RuntimeMCPService()
    router_dispatch_service = RouterDispatchMCPService()

    server.register_tool(
        name="read_system_runtime_state",
        description="Read the current system runtime state.",
        handler=service.read_system_runtime_state,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "system_state"],
    )

    server.register_tool(
        name="read_llm_runtime_state",
        description="Read the current LLM runtime state.",
        handler=service.read_llm_runtime_state,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "llm_state"],
    )

    server.register_tool(
        name="read_recent_chat_history",
        description="Read the recent chat history from runtime output.",
        handler=service.read_recent_chat_history,
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20},
            },
        },
        tags=["runtime", "chat_history"],
    )

    server.register_tool(
        name="read_latest_response",
        description="Read the latest assistant response payload.",
        handler=service.read_latest_response,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "response"],
    )

    server.register_tool(
        name="read_latest_tts",
        description="Read the latest TTS payload.",
        handler=service.read_latest_tts,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "tts"],
    )

    server.register_tool(
        name="read_latest_decision",
        description="Read the latest decision payload.",
        handler=service.read_latest_decision,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "decision"],
    )

    server.register_tool(
        name="read_router_dispatch_status",
        description="Read the current router_dispatch status payload.",
        handler=router_dispatch_service.read_router_dispatch_status,
        input_schema={"type": "object", "properties": {}},
        tags=["runtime", "router_dispatch", "status"],
    )

    server.register_tool(
        name="tail_router_dispatch_queue",
        description="Read the latest entries from a router_dispatch queue.",
        handler=router_dispatch_service.tail_router_dispatch_queue,
        input_schema={
            "type": "object",
            "properties": {
                "queue": {
                    "type": "string",
                    "enum": ["router_input", "action", "response"],
                },
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["queue"],
        },
        tags=["runtime", "router_dispatch", "queue", "read"],
    )
