from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class SessionEventsReader:
    events_path: str | Path

    def read(self, limit: int | None = None) -> list[EventInput]:
        path = Path(self.events_path)
        if not path.exists():
            return []

        events: list[EventInput] = []
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = str(payload.get("text") or payload.get("event_text") or "").strip()
                if not text:
                    continue

                event_type = str(payload.get("event_type") or payload.get("type") or "note").strip() or "note"
                ts = self._coerce_float(payload.get("ts"))
                event_id = self._coerce_str(payload.get("event_id") or payload.get("id"))
                source = str(payload.get("source") or "session_event").strip() or "session_event"

                metadata = {}
                raw_metadata = payload.get("metadata")
                if isinstance(raw_metadata, dict):
                    metadata = raw_metadata

                events.append(
                    EventInput(
                        event_type=event_type,
                        text=text,
                        ts=ts,
                        event_id=event_id,
                        source=source,
                        metadata=metadata,
                    )
                )

        if limit is not None and limit > 0:
            return events[-limit:]
        return events

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