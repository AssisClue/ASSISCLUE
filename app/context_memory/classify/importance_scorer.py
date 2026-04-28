from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ImportanceScorer:
    def score(self, text: str, kind: str = "", source: str = "") -> float:
        cleaned = text.strip()
        if not cleaned:
            return 0.0

        score = 0.20
        lowered = cleaned.lower()

        if len(cleaned) >= 30:
            score += 0.15
        if len(cleaned.split()) >= 8:
            score += 0.10

        if kind in {"persistent_fact", "preference", "project_context"}:
            score += 0.20

        if kind in {"issue", "coding_issue"}:
            score += 0.20

        if source in {"screenshot_note", "file_context"}:
            score += 0.10

        if any(token in lowered for token in ("important", "remember", "critical", "urgent")):
            score += 0.15

        if any(token in lowered for token in ("error", "exception", "traceback", "failed", "failure")):
            score += 0.10

        return min(score, 1.0)