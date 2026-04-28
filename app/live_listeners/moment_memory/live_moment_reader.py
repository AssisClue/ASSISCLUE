from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LiveMomentReader:
    """
    Reader dedicated to live moments.

    Unlike TranscriptReader, this reader treats a live moment as valid when it
    has:
    - event_id
    - paragraph

    It keeps its own cursor file and only advances after reading/parsing lines.
    """

    def __init__(self, *, transcript_path: Path, cursor_path: Path) -> None:
        self.transcript_path = Path(transcript_path)
        self.cursor_path = Path(cursor_path)

    def _load_cursor(self) -> int:
        if not self.cursor_path.exists() or not self.cursor_path.is_file():
            return 0

        try:
            raw = json.loads(self.cursor_path.read_text(encoding="utf-8"))
        except Exception:
            return 0

        value = raw.get("line_index", 0) if isinstance(raw, dict) else 0
        try:
            return max(0, int(value))
        except Exception:
            return 0

    def _save_cursor(self, line_index: int) -> None:
        self.cursor_path.parent.mkdir(parents=True, exist_ok=True)
        self.cursor_path.write_text(
            json.dumps({"line_index": int(line_index)}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _is_valid_live_moment(self, payload: dict[str, Any]) -> bool:
        event_id = str(payload.get("event_id", "")).strip()
        paragraph = str(payload.get("paragraph", "")).strip()
        return bool(event_id and paragraph)

    def read_new_records(self) -> list[dict[str, Any]]:
        if not self.transcript_path.exists() or not self.transcript_path.is_file():
            return []

        try:
            lines = self.transcript_path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return []

        start_index = self._load_cursor()
        if start_index >= len(lines):
            return []

        new_records: list[dict[str, Any]] = []

        for line in lines[start_index:]:
            line = line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except Exception:
                continue

            if not isinstance(payload, dict):
                continue

            if self._is_valid_live_moment(payload):
                new_records.append(payload)

        self._save_cursor(len(lines))
        return new_records