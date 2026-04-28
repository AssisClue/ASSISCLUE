from __future__ import annotations

from app.live_listeners.primary_listener.wakeword_matcher import normalize_text


def _contains_any(text: str, variants: list[str]) -> bool:
    return any(item in text for item in variants)


def _matches_simple_phrase(text: str, variants: list[str]) -> bool:
    normalized = normalize_text(text)
    for item in variants:
        phrase = normalize_text(item)
        if normalized == phrase:
            return True
    return False


def match_simple_question(text: str) -> dict[str, str] | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    if _matches_simple_phrase(normalized, ["what time is it", "tell me the time", "current time"]):
        return {"intent": "current_time"}

    if _matches_simple_phrase(normalized, ["what day is it", "what is today", "today date", "what's today's date"]):
        return {"intent": "current_date"}

    if _contains_any(normalized, ["are you there", "you there", "can you hear me"]):
        return {"intent": "presence_check"}

    if _contains_any(normalized, ["what mode", "current mode", "which mode"]):
        return {"intent": "system_mode_unknown"}

    if _contains_any(normalized, ["who are you", "what are you"]):
        return {"intent": "identity"}

    return None
