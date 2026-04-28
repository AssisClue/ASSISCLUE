from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class LiveMomentHistoryReader:
    history_path: str | Path

    def read_from_offset(self, start_offset: int) -> tuple[list[EventInput], int]:
        path = Path(self.history_path)
        if not path.exists():
            return [], max(0, int(start_offset or 0))

        items: list[EventInput] = []
        current_offset = max(0, int(start_offset or 0))
        file_size = path.stat().st_size
        if current_offset > file_size:
            current_offset = file_size

        encoding = "utf-8-sig" if current_offset == 0 else "utf-8"
        with path.open("r", encoding=encoding) as handle:
            handle.seek(current_offset)
            while True:
                line_start = handle.tell()
                raw_line = handle.readline()
                if raw_line == "":
                    break
                if not raw_line.endswith("\n"):
                    handle.seek(line_start)
                    break

                current_offset = handle.tell()
                item = self._parse_line(raw_line)
                if item is not None:
                    items.append(item)

        return items, current_offset

    def _parse_line(self, raw_line: str) -> EventInput | None:
        line = raw_line.strip().lstrip("\ufeff")
        if not line:
            return None

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return None

        text = str(payload.get("paragraph") or payload.get("text") or "").strip()
        if not text:
            return None

        event_type = str(payload.get("intent_type") or payload.get("event_type") or "live_moment").strip()
        event_id = str(payload.get("event_id") or "").strip() or None
        ts = self._coerce_float(payload.get("ts"))
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}

        return EventInput(
            event_type=event_type or "live_moment",
            text=text,
            ts=ts,
            event_id=event_id,
            source="live_moment",
            metadata={
                **metadata,
                "source_session_id": str(payload.get("source_session_id") or "").strip(),
                "source_event_ids": list(payload.get("source_event_ids") or []),
            },
        )

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
