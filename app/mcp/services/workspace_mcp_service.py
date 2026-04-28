from __future__ import annotations

from dataclasses import dataclass, field

from app.mcp.adapters.workspace_adapter import WorkspaceAdapter
from app.mcp.schemas import MCPToolResult


@dataclass(slots=True)
class WorkspaceMCPService:
    """
    MCP-facing workspace service.

    Responsibilities:
    - expose file/note helpers through normalized MCP results
    - keep MCP callers decoupled from raw helper functions
    """

    adapter: WorkspaceAdapter = field(default_factory=WorkspaceAdapter)

    def read_text_file(self, *, path: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="read_text_file",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        try:
            text = self.adapter.read_text_file(path=clean_path)
        except Exception as exc:
            return MCPToolResult(
                ok=False,
                tool_name="read_text_file",
                message="File read failed.",
                error_code="read_text_file_error",
                data={"path": clean_path},
                meta={"exception": f"{type(exc).__name__}: {exc}"},
            )

        return MCPToolResult(
            ok=True,
            tool_name="read_text_file",
            message="Text file loaded.",
            data={"path": clean_path, "text": text},
        )

    def read_text_file_safe(self, *, path: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="read_text_file_safe",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        text = self.adapter.read_text_file_safe(path=clean_path)
        return MCPToolResult(
            ok=True,
            tool_name="read_text_file_safe",
            message="Safe text file read completed.",
            data={"path": clean_path, "text": text},
        )

    def read_python_file(self, *, path: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="read_python_file",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        data = self.adapter.read_python_file(path=clean_path)
        return MCPToolResult(
            ok=True,
            tool_name="read_python_file",
            message="Python file loaded.",
            data=data,
        )

    def read_json_file(self, *, path: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="read_json_file",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        data = self.adapter.read_json_file(path=clean_path)
        return MCPToolResult(
            ok=True,
            tool_name="read_json_file",
            message="JSON file read completed.",
            data=data,
            error_code=str(data.get("error") or ""),
        )

    def append_note(self, *, path: str, text: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        clean_text = str(text or "")

        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="append_note",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        self.adapter.append_note(path=clean_path, text=clean_text)
        return MCPToolResult(
            ok=True,
            tool_name="append_note",
            message="Note appended.",
            data={"path": clean_path},
        )

    def overwrite_note(self, *, path: str, text: str) -> MCPToolResult:
        clean_path = str(path or "").strip()
        clean_text = str(text or "")

        if not clean_path:
            return MCPToolResult(
                ok=False,
                tool_name="overwrite_note",
                message="Path cannot be empty.",
                error_code="empty_path",
                data={"path": clean_path},
            )

        self.adapter.overwrite_note(path=clean_path, text=clean_text)
        return MCPToolResult(
            ok=True,
            tool_name="overwrite_note",
            message="Note overwritten.",
            data={"path": clean_path},
        )