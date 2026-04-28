from __future__ import annotations

from app.mcp.services.capabilities_mcp_service import CapabilitiesMCPService


def register_capabilities_tools(server) -> None:
    service = CapabilitiesMCPService()

    server.register_tool(
        name="list_capabilities",
        description="List app capabilities exposed by the capability registry.",
        handler=service.list_capabilities,
        input_schema={"type": "object", "properties": {}},
        tags=["capabilities", "read"],
    )

    server.register_tool(
        name="get_capability_by_action_name",
        description="Get one capability by action_name.",
        handler=service.get_capability_by_action_name,
        input_schema={
            "type": "object",
            "properties": {
                "action_name": {"type": "string"},
            },
            "required": ["action_name"],
        },
        tags=["capabilities", "read"],
    )