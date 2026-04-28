from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .cursor_store import load_cursor, save_cursor
from .listener_paths import ensure_listener_runtime_dirs
from .listener_record_utils import get_record_event_id, is_minimal_transcript_record


class TranscriptReader:
    def __init__(self, transcript_path: Path, cursor_path: Path) -> None:
        self.transcript_path = transcript_path
        self.cursor_path = cursor_path

    def read_new_records(self) -> list[dict[str, Any]]:
        ensure_listener_runtime_dirs()

        cursor = load_cursor(self.cursor_path)
        start_offset = int(cursor.get("byte_offset", 0) or 0)
        previous_event_id = str(cursor.get("last_event_id", "") or "")

        if not self.transcript_path.exists():
            return []

        file_size = self.transcript_path.stat().st_size
        if start_offset > file_size:
            start_offset = file_size
            previous_event_id = ""
            save_cursor(
                self.cursor_path,
                byte_offset=start_offset,
                last_event_id=previous_event_id,
            )

        records: list[dict[str, Any]] = []
        final_offset = start_offset
        last_event_id = previous_event_id

        with self.transcript_path.open("r", encoding="utf-8") as f:
            f.seek(start_offset)

            while True:
                line = f.readline()
                if not line:
                    break

                final_offset = f.tell()
                stripped = line.strip()
                if not stripped:
                    continue

                try:
                    record = json.loads(stripped)
                except Exception:
                    continue

                if not is_minimal_transcript_record(record):
                    continue

                last_event_id = get_record_event_id(record)
                records.append(record)

        if final_offset != start_offset or last_event_id != previous_event_id:
            save_cursor(
                self.cursor_path,
                byte_offset=final_offset,
                last_event_id=last_event_id,
            )

        return records

    def peek_cursor(self) -> dict[str, Any]:
        return load_cursor(self.cursor_path)
