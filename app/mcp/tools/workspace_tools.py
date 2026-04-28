from __future__ import annotations

from app.mcp.services.workspace_mcp_service import WorkspaceMCPService


def register_workspace_tools(server) -> None:
    service = WorkspaceMCPService()

    server.register_tool(
        name="read_text_file",
        description="Read a UTF-8 text file.",
        handler=service.read_text_file,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
        tags=["workspace", "file", "read"],
    )

    server.register_tool(
        name="read_text_file_safe",
        description="Read a UTF-8 text file safely, returning empty text on failure.",
        handler=service.read_text_file_safe,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
        tags=["workspace", "file", "read"],
    )

    server.register_tool(
        name="read_python_file",
        description="Read a Python source file as text with language metadata.",
        handler=service.read_python_file,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
        tags=["workspace", "file", "python", "read"],
    )

    server.register_tool(
        name="read_json_file",
        description="Read and parse a JSON file with safe fallback.",
        handler=service.read_json_file,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
        tags=["workspace", "file", "json", "read"],
    )

    server.register_tool(
        name="append_note",
        description="Append text to a note file.",
        handler=service.append_note,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["path", "text"],
        },
        tags=["workspace", "note", "write"],
    )

    server.register_tool(
        name="overwrite_note",
        description="Overwrite a note file with new text.",
        handler=service.overwrite_note,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["path", "text"],
        },
        tags=["workspace", "note", "write"],
    )