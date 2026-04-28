from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FactExtractor:
    def extract(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        lowered = cleaned.lower()
        facts: list[str] = []

        triggers = (
            "user prefers",
            "user likes",
            "user wants",
            "project is",
            "project uses",
            "we are using",
            "we use",
            "mem0",
            "qdrant",
            "fallback",
        )

        for trigger in triggers:
            if trigger in lowered:
                facts.append(cleaned)
                break

        return facts