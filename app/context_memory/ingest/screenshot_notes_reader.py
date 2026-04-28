from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.context_memory.contracts.input_types import ScreenshotNoteInput


@dataclass(slots=True)
class ScreenshotNotesReader:
    notes_path: str | Path

    def read(self, limit: int | None = None) -> list[ScreenshotNoteInput]:
        path = Path(self.notes_path)
        if not path.exists():
            return []

        notes: list[ScreenshotNoteInput] = []
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = str(payload.get("text") or payload.get("note") or "").strip()
                if not text:
                    continue

                ts = self._coerce_float(payload.get("ts"))
                screenshot_id = self._coerce_str(payload.get("screenshot_id") or payload.get("id"))
                source = str(payload.get("source") or "screenshot_note").strip() or "screenshot_note"

                metadata = {}
                raw_metadata = payload.get("metadata")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata

                notes.append(
                    ScreenshotNoteInput(
                        text=text,
                        ts=ts,
                        screenshot_id=screenshot_id,
                        source=source,
                        metadata=metadata,
                    )
                )

        if limit is not None and limit > 0:
            return notes[-limit:]
        return notes

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_str(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None