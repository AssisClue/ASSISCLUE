from __future__ import annotations

from .administrative_listener_config import QUESTION_HINTS


def detect_present_intent(paragraph: str) -> str:
    text = " ".join((paragraph or "").strip().lower().split())
    if not text:
        return "ignore"

    words = text.split()
    if not words:
        return "ignore"

    if "?" in paragraph:
        return "response_candidate"

    if words[0] in QUESTION_HINTS:
        return "response_candidate"

    if len(words) >= 6:
        return "context_only"

    return "ignore"