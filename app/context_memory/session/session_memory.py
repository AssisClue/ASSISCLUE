from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class SessionMemory:
    session_id: str = "default_session"
    events: list[EventInput] = field(default_factory=list)

    def add_event(self, event: EventInput) -> None:
        if not event.text.strip():
            return
        self.events.append(event)

    def add_text_event(
        self,
        text: str,
        event_type: str = "note",
        ts: float | None = None,
        event_id: str | None = None,
        source: str = "session_event",
    ) -> None:
        cleaned = text.strip()
        if not cleaned:
            return

        self.events.append(
            EventInput(
                event_type=event_type,
                text=cleaned,
                ts=ts,
                event_id=event_id,
                source=source,
            )
        )

    def get_recent(self, limit: int = 20) -> list[EventInput]:
        if limit <= 0:
            return []
        return self.events[-limit:]

    def get_recent_texts(self, limit: int = 20) -> list[str]:
        return [item.text for item in self.get_recent(limit=limit)]

    def clear(self) -> None:
        self.events.clear()

    def size(self) -> int:
        return len(self.events)