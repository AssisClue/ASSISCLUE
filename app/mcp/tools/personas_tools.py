from __future__ import annotations

from app.mcp.services.personas_mcp_service import PersonasMCPService


def register_personas_tools(server) -> None:
    service = PersonasMCPService()

    server.register_tool(
        name="list_personas",
        description="List safe persona summaries from app/personas.",
        handler=service.list_personas,
        input_schema={"type": "object", "properties": {}},
        tags=["personas", "read"],
    )

    server.register_tool(
        name="get_persona",
        description="Get one persona by persona_id.",
        handler=service.get_persona,
        input_schema={
            "type": "object",
            "properties": {
                "persona_id": {"type": "string"},
            },
            "required": ["persona_id"],
        },
        tags=["personas", "read"],
    )

    server.register_tool(
        name="get_active_persona_id",
        description="Read the currently active persona id from runtime state.",
        handler=service.get_active_persona_id,
        input_schema={"type": "object", "properties": {}},
        tags=["personas", "read"],
    )