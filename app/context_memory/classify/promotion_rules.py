from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PromotionRules:
    threshold: float = 0.70

    def should_promote(
        self,
        text: str,
        kind: str = "",
        importance: float = 0.0,
    ) -> bool:
        cleaned = text.strip()
        if not cleaned:
            return False

        lowered = cleaned.lower()

        if kind in {"persistent_fact", "preference", "project_context"} and importance >= 0.45:
            return True

        if kind in {"issue", "coding_issue"} and importance >= 0.60:
            return True

        if len(cleaned) < 25:
            return False

        score = importance

        if any(token in lowered for token in ("remember", "important", "prefer", "likes", "project")):
            score += 0.20

        if len(cleaned.split()) >= 10:
            score += 0.10

        return score >= self.threshold