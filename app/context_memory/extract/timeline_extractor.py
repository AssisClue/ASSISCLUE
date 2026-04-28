from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TimelineExtractor:
    def extract(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        lowered = cleaned.lower()
        hits: list[str] = []

        patterns = (
            "today",
            "yesterday",
            "last week",
            "this week",
            "hoy",
            "ayer",
            "semana pasada",
            "esta semana",
            "meeting",
            "reunión",
        )

        for pattern in patterns:
            if pattern in lowered:
                hits.append(cleaned)
                break

        return hits