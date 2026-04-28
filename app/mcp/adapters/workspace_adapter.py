from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from app.tools.file_reader import read_text_file, safe_read_text_file
from app.tools.note_writer import append_note, overwrite_note


@dataclass(slots=True)
class WorkspaceAdapter:
    """
    MCP-facing adapter for simple workspace file and note operations.

    Phase 1/2 stays intentionally local-file oriented and minimal.
    """

    def read_text_file(self, *, path: str) -> str:
        return read_text_file(path)

    def read_text_file_safe(self, *, path: str) -> str:
        return safe_read_text_file(path)

    def read_python_file(self, *, path: str) -> dict[str, str]:
        text = safe_read_text_file(path)
        return {
            "path": str(Path(path)),
            "language": "python",
            "text": text,
        }

    def read_json_file(self, *, path: str) -> dict:
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            return {
                "path": str(file_path),
                "exists": False,
                "data": {},
            }

        try:
            raw = file_path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except Exception:
            return {
                "path": str(file_path),
                "exists": True,
                "data": {},
                "error": "invalid_json",
            }

        return {
            "path": str(file_path),
            "exists": True,
            "data": parsed if isinstance(parsed, dict) else parsed,
        }

    def append_note(self, *, path: str, text: str) -> dict[str, str]:
        append_note(path, text)
        return {
            "path": str(Path(path)),
            "mode": "append",
            "status": "ok",
        }

    def overwrite_note(self, *, path: str, text: str) -> dict[str, str]:
        overwrite_note(path, text)
        return {
            "path": str(Path(path)),
            "mode": "overwrite",
            "status": "ok",
        }