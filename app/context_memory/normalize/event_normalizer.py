from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.input_types import EventInput
from app.context_memory.normalize.text_cleaner import TextCleaner


@dataclass(slots=True)
class EventNormalizer:
    text_cleaner: TextCleaner

    def normalize(self, event: EventInput) -> EventInput:
        return EventInput(
            event_type=event.event_type.strip().lower() or "note",
            text=self.text_cleaner.clean(event.text),
            ts=event.ts,
            event_id=(event.event_id.strip() if event.event_id else None),
            source=event.source.strip() or "session_event",
            metadata=dict(event.metadata),
        )