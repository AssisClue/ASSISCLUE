from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.mcp.server import MCPServer
    
from app.mcp.services.memory_mcp_service import MemoryMCPService


def register_memory_tools(server) -> None:
    service = MemoryMCPService()

    server.register_tool(
        name="search_memory",
        description="Search memory using the current context-memory service layer.",
        handler=service.search_memory,
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
                "preferred_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                },
            },
            "required": ["query"],
        },
        tags=["memory", "search"],
    )

    server.register_tool(
        name="get_recent_context",
        description="Load the recent context snapshot.",
        handler=service.get_recent_context,
        input_schema={"type": "object", "properties": {}},
        tags=["memory", "recent_context"],
    )

    server.register_tool(
        name="get_live_context",
        description="Load the live context snapshot.",
        handler=service.get_live_context,
        input_schema={"type": "object", "properties": {}},
        tags=["memory", "live_context"],
    )

    server.register_tool(
        name="get_user_profile_context",
        description="Load the user profile context snapshot.",
        handler=service.get_user_profile_context,
        input_schema={"type": "object", "properties": {}},
        tags=["memory", "profile"],
    )

    server.register_tool(
        name="get_task_context",
        description="Build a task context packet using the context-memory service.",
        handler=service.get_task_context,
        input_schema={
            "type": "object",
            "properties": {
                "task_type": {"type": "string"},
                "query": {"type": "string", "default": ""},
                "project_name": {"type": "string", "default": ""},
                "preferred_sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": [],
                },
            },
            "required": ["task_type"],
        },
        tags=["memory", "task_context"],
    )

    server.register_tool(
        name="list_user_spaces",
        description="List available user spaces.",
        handler=service.list_user_spaces,
        input_schema={"type": "object", "properties": {}},
        tags=["memory", "user_spaces"],
    )

    server.register_tool(
        name="get_user_space",
        description="Search inside one user space.",
        handler=service.get_user_space,
        input_schema={
            "type": "object",
            "properties": {
                "space_id": {"type": "string"},
                "query": {"type": "string", "default": ""},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["space_id"],
        },
        tags=["memory", "user_spaces"],
    )