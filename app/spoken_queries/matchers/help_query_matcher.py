from __future__ import annotations

from pathlib import Path

from app.live_listeners.primary_listener.wakeword_matcher import normalize_text
from app.system_support.system_runtime_state import is_help_explain_capture_enabled


PROJECT_ROOT = Path(__file__).resolve().parents[3]


_HELP_ALWAYS_PREFIXES = (
    "help",
)

_HELP_EXPLAIN_PREFIXES = (
    "explain",
    "explicar",
    "explica",
    "explicame",
    "explícame",
    "what is",
    "what are",
    "que es",
    "qué es",
    "que son",
    "qué son",
)


def is_help_query(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False

    if any(
        normalized == prefix or normalized.startswith(prefix + " ")
        for prefix in _HELP_ALWAYS_PREFIXES
    ):
        return True

    if not is_help_explain_capture_enabled(PROJECT_ROOT):
        return False

    return any(
        normalized == prefix or normalized.startswith(prefix + " ")
        for prefix in _HELP_EXPLAIN_PREFIXES
    )