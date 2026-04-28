from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TopicExtractor:
    known_topics: tuple[str, ...] = (
        "memory",
        "context",
        "screenshot",
        "coding",
        "timeline",
        "meetings",
        "project",
        "retrieval",
        "backend",
        "profile",
        "runtime",
        "error",
    )

    def extract(self, text: str) -> list[str]:
        lowered = text.strip().lower()
        if not lowered:
            return []

        found: list[str] = []
        for topic in self.known_topics:
            if topic in lowered and topic not in found:
                found.append(topic)

        return found