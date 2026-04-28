from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemoryKindClassifier:
    def classify(self, text: str, source: str = "") -> str:
        lowered = text.strip().lower()
        lowered_source = source.strip().lower()

        if not lowered:
            return "discard"

        if lowered_source == "screenshot_note":
            if any(token in lowered for token in ("error", "traceback", "exception", "line ", "syntax")):
                return "coding_issue"
            return "screenshot_context"

        if lowered_source == "file_context":
            return "file_context"

        if any(token in lowered for token in ("prefiero", "prefer", "likes", "likes to", "wants", "user prefers")):
            return "preference"

        if any(token in lowered for token in ("project", "proyecto", "repo", "branch", "module", "feature")):
            return "project_context"

        if any(token in lowered for token in ("today", "hoy", "ayer", "last week", "semana pasada", "meeting", "reunión")):
            return "timeline"

        if any(token in lowered for token in ("error", "failed", "failure", "problem", "bug", "issue")):
            return "issue"

        if any(token in lowered for token in ("remember", "important", "recordar", "importante")):
            return "persistent_fact"

        return "general_memory"