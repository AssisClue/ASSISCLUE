from __future__ import annotations

from pathlib import Path
import json

from app.mcp.server import create_mcp_server


def main() -> None:
    server = create_mcp_server()
    note_path = "runtime/mcp_test_note.txt"
    json_path = "runtime/mcp_test_data.json"
    py_path = "app/mcp/server.py"

    result = server.call_tool("read_text_file_safe", path="README.md")
    assert result.tool_name == "read_text_file_safe"
    assert result.ok is True
    assert isinstance(result.data, dict)
    assert "text" in result.data

    result = server.call_tool("overwrite_note", path=note_path, text="hello from mcp")
    assert result.tool_name == "overwrite_note"
    assert result.ok is True

    result = server.call_tool("append_note", path=note_path, text="second line")
    assert result.tool_name == "append_note"
    assert result.ok is True

    result = server.call_tool("read_text_file_safe", path=note_path)
    assert result.tool_name == "read_text_file_safe"
    assert result.ok is True
    text = str(result.data.get("text") or "")
    assert "hello from mcp" in text
    assert "second line" in text

    Path(json_path).write_text(json.dumps({"alpha": 1, "beta": "ok"}), encoding="utf-8")
    result = server.call_tool("read_json_file", path=json_path)
    assert result.tool_name == "read_json_file"
    assert result.ok is True
    assert result.data["exists"] is True
    assert result.data["data"]["alpha"] == 1

    result = server.call_tool("read_python_file", path=py_path)
    assert result.tool_name == "read_python_file"
    assert result.ok is True
    assert result.data["language"] == "python"
    assert "create_mcp_server" in str(result.data["text"])

    path_obj = Path(note_path)
    assert path_obj.exists()

    print("test_workspace_tools=ok")


if __name__ == "__main__":
    main()