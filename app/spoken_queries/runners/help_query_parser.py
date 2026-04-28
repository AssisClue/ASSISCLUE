from __future__ import annotations

from dataclasses import dataclass

from app.live_listeners.primary_listener.wakeword_matcher import normalize_text


_HELP_PREFIXES = (
    "help",
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

_NOISE_PREFIXES = (
    "about",
    "sobre",
    "for",
    "de",
    "del",
    "la",
    "el",
)


@dataclass(slots=True)
class HelpQueryIntent:
    cleaned_query: str
    is_menu_request: bool
    explain_capture_action: str


def parse_help_query(text: str) -> HelpQueryIntent:
    normalized = normalize_text(text)

    explain_capture_action = ""
    if normalized in (
        "help explain on",
        "help capture on",
        "help explain capture on",
        "enable help explain",
        "enable help explain capture",
        "turn on help explain",
        "turn on help explain capture",
    ):
        explain_capture_action = "on"
    elif normalized in (
        "help explain off",
        "help capture off",
        "help explain capture off",
        "disable help explain",
        "disable help explain capture",
        "turn off help explain",
        "turn off help explain capture",
    ):
        explain_capture_action = "off"

    cleaned = normalized
    for prefix in _HELP_PREFIXES:
        if cleaned == prefix:
            cleaned = ""
            break
        if cleaned.startswith(prefix + " "):
            cleaned = cleaned[len(prefix):].strip()
            break

    for prefix in _NOISE_PREFIXES:
        if cleaned.startswith(prefix + " "):
            cleaned = cleaned[len(prefix):].strip()

    is_menu_request = cleaned in (
        "",
        "menu",
        "help menu",
        "main menu",
        "options",
        "topics",
    )

    return HelpQueryIntent(
        cleaned_query=cleaned.strip(),
        is_menu_request=is_menu_request,
        explain_capture_action=explain_capture_action,
    )