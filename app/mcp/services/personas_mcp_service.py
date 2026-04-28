from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.personas_adapter import PersonasAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class PersonasMCPService:
    """
    MCP-facing service for personas.
    """

    adapter: PersonasAdapter = field(default_factory=PersonasAdapter)

    def list_personas(self) -> MCPToolResult:
        data = self.adapter.list_personas()
        return MCPToolResult(
            ok=True,
            tool_name="list_personas",
            message="Personas loaded.",
            data=data,
        )

    def get_persona(self, *, persona_id: str) -> MCPToolResult:
        clean_persona_id = str(persona_id or "").strip()
        if not clean_persona_id:
            return MCPToolResult(
                ok=False,
                tool_name="get_persona",
                message="Persona id cannot be empty.",
                error_code="empty_persona_id",
                data={"persona_id": clean_persona_id},
            )

        data = self.adapter.get_persona(persona_id=clean_persona_id)
        return MCPToolResult(
            ok=True,
            tool_name="get_persona",
            message="Persona lookup completed.",
            data=data,
        )

    def get_active_persona_id(self) -> MCPToolResult:
        data = self.adapter.get_active_persona_id()
        return MCPToolResult(
            ok=True,
            tool_name="get_active_persona_id",
            message="Active persona id loaded.",
            data=data,
        )