from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.runtime_adapter import RuntimeAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class RuntimeMCPService:
    """
    MCP-facing runtime service.

    Responsibilities:
    - expose runtime state through normalized MCPToolResult values
    - keep MCP callers decoupled from system_support implementation details
    """

    adapter: RuntimeAdapter = field(default_factory=RuntimeAdapter)

    def read_system_runtime_state(self) -> MCPToolResult:
        data = self.adapter.read_system_runtime_state()
        return MCPToolResult(
            ok=True,
            tool_name="read_system_runtime_state",
            message="System runtime state loaded.",
            data=data,
        )

    def read_llm_runtime_state(self) -> MCPToolResult:
        try:
            data = self.adapter.read_llm_runtime_state()
            return MCPToolResult(
                ok=True,
                tool_name="read_llm_runtime_state",
                message="LLM runtime state loaded.",
                data=data,
            )
        except Exception as exc:
            return MCPToolResult(
                ok=False,
                tool_name="read_llm_runtime_state",
                message="LLM runtime state failed.",
                error_code="llm_runtime_state_error",
                meta={"exception": f"{type(exc).__name__}: {exc}"},
            )

    def read_recent_chat_history(self, *, limit: int = 20) -> MCPToolResult:
        clean_limit = max(1, int(limit or 20))
        data = self.adapter.read_recent_chat_history(limit=clean_limit)
        return MCPToolResult(
            ok=True,
            tool_name="read_recent_chat_history",
            message="Recent chat history loaded.",
            data={
                "items": data,
                "limit": clean_limit,
                "count": len(data),
            },
        )

    def read_latest_response(self) -> MCPToolResult:
        data = self.adapter.read_latest_response()
        return MCPToolResult(
            ok=True,
            tool_name="read_latest_response",
            message="Latest response loaded.",
            data=data,
        )

    def read_latest_tts(self) -> MCPToolResult:
        data = self.adapter.read_latest_tts()
        return MCPToolResult(
            ok=True,
            tool_name="read_latest_tts",
            message="Latest TTS payload loaded.",
            data=data,
        )

    def read_latest_decision(self) -> MCPToolResult:
        data = self.adapter.read_latest_decision()
        return MCPToolResult(
            ok=True,
            tool_name="read_latest_decision",
            message="Latest decision loaded.",
            data=data,
        )