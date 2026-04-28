from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProjectExtractor:
    known_projects: tuple[str, ...] = (
        "ASSISCLUE",
        "livekit",
        "mem0",
        "qdrant",
        "tts",
        "stt",
        "assistant_core",
    )

    def extract(self, text: str) -> str | None:
        lowered = text.strip().lower()
        if not lowered:
            return None

        for project_name in self.known_projects:
            if project_name in lowered:
                return project_name

        return None