from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class SessionRollup:
    def build_lines(self, events: list[EventInput], max_items: int = 12) -> list[str]:
        events_sorted = sorted(events, key=lambda event: event.ts or 0.0, reverse=True)

        lines: list[str] = []
        for event in events_sorted:
            cleaned = event.text.strip()
            if not cleaned:
                continue

            lines.append(f"[{event.event_type}] {cleaned}")
            if len(lines) >= max_items:
                break

        return lines