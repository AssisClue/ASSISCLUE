from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProfileExtractor:
    def extract(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        lowered = cleaned.lower()
        hits: list[str] = []

        patterns = (
            "i prefer",
            "prefer",
            "me gusta",
            "prefiero",
            "quiero",
            "respuestas cortas",
            "clear answers",
            "organized",
            "short answers",
        )

        for pattern in patterns:
            if pattern in lowered:
                hits.append(cleaned)
                break

        return hits