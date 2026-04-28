from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.input_types import EventInput
from app.context_memory.normalize.dedupe_keys import build_dedupe_key


@dataclass(slots=True)
class SessionCompactor:
    def compact(self, events: list[EventInput], max_items: int = 50) -> list[EventInput]:
        deduped: list[EventInput] = []
        seen: set[str] = set()

        for event in events:
            key = build_dedupe_key(text=event.text, source=event.source, kind=event.event_type)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(event)

        deduped.sort(key=lambda event: event.ts or 0.0, reverse=True)
        return deduped[:max_items]
    