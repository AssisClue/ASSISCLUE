from __future__ import annotations

from app.live_listeners.primary_listener.memory_flag_matcher import detect_use_memory_flag
from app.live_listeners.primary_listener.wakeword_matcher import normalize_text
from app.spoken_queries.runners.memory_query_hint_parser import is_persona_lookup_request


def requires_memory_runner(text: str, *, flags: dict | None = None) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False

    flags = flags or {}

    if bool(flags.get("use_memory", False)):
        return True

    if detect_use_memory_flag(normalized):
        return True

    if is_persona_lookup_request(normalized, flags=flags):
        return True

    return False