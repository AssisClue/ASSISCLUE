from __future__ import annotations

from .wakeword_matcher import normalize_text


MEMORY_FLAG_ALIASES = (
    "use memory",
    "memory",
    "memo",
    "mem",
    "memoria",
    "use memo",
    "use memoria",
    "check memory",
    "with memory",
    "use context",
    "check context",
)


def detect_use_memory_flag(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False

    for alias in MEMORY_FLAG_ALIASES:
        candidate = normalize_text(alias)
        if candidate and candidate in normalized:
            return True

    return False


def strip_memory_flag_phrases(text: str) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return ""

    cleaned = normalized
    for alias in MEMORY_FLAG_ALIASES:
        candidate = normalize_text(alias)
        if not candidate:
            continue
        cleaned = cleaned.replace(candidate, " ")

    return normalize_text(cleaned)
