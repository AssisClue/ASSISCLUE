from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class SessionWindowManager:
    recent_limit: int = 50
    recent_events: list[EventInput] = field(default_factory=list)

    def push(self, event: EventInput) -> None:
        if not event.text.strip():
            return

        self.recent_events.append(event)
        if len(self.recent_events) > self.recent_limit:
            self.recent_events = self.recent_events[-self.recent_limit :]

    def extend(self, events: list[EventInput]) -> None:
        for event in events:
            self.push(event)

    def get_recent(self, limit: int | None = None) -> list[EventInput]:
        resolved_limit = self.recent_limit if limit is None else max(limit, 0)
        if resolved_limit == 0:
            return []
        return self.recent_events[-resolved_limit:]

    def get_recent_texts(self, limit: int | None = None) -> list[str]:
        return [item.text for item in self.get_recent(limit=limit)]

    def clear(self) -> None:
        self.recent_events.clear()

    def size(self) -> int:
        return len(self.recent_events)