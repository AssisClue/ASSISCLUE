from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SourceClassifier:
    def classify(self, source: str) -> str:
        lowered = source.strip().lower()

        if not lowered:
            return "unknown"

        if "chat" in lowered:
            return "chat"
        if "event" in lowered:
            return "event"
        if "screenshot" in lowered:
            return "screenshot"
        if "file" in lowered:
            return "file"
        if "runtime" in lowered:
            return "runtime"

        return lowered