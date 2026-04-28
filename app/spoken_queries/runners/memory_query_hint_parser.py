from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.contracts.task_types import TaskContextHint
from app.live_listeners.primary_listener.memory_flag_matcher import detect_use_memory_flag
from app.live_listeners.primary_listener.memory_flag_matcher import strip_memory_flag_phrases
from app.live_listeners.primary_listener.wakeword_matcher import normalize_text


_SOURCE_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("prompts", "prompt"), "user_spaces.prompts"),
    (("rules", "rule"), "user_spaces.rules"),
    (("notes", "note"), "user_spaces.notes"),
    (("help", "menu", "glosary", "glossary", "manual", "explain", "explicar"), "user_spaces.help"),
    (("personas", "persona", "profiles", "profile"), "personas"),
)

_QUERY_PREFIXES = (
    "explicar",
    "explain",
    "search for",
    "search",
    "check",
    "look in",
    "look for",
    "look up",
    "look",
    "find",
    "show",
    "tell me about",
    "tell me",
    "do we have a",
    "do we have",
    "is there a",
    "is there",
)


@dataclass(slots=True)
class MemoryQueryIntent:
    cleaned_query: str
    hint: TaskContextHint
    source_key: str


def _strip_prefixes(text: str) -> str:
    cleaned = str(text or "").strip()
    for prefix in _QUERY_PREFIXES:
        if cleaned == prefix:
            return ""
        if cleaned.startswith(prefix + " "):
            return cleaned[len(prefix):].strip()
    return cleaned


def _strip_noise_words(text: str) -> str:
    cleaned = normalize_text(text)
    for prefix in ("about ", "for ", "named ", "called "):
        if cleaned.startswith(prefix):
            return cleaned[len(prefix):].strip()
    return cleaned


def parse_memory_query_intent(text: str) -> MemoryQueryIntent:
    normalized = normalize_text(text)
    without_memory_flag = strip_memory_flag_phrases(normalized) or normalized

    source_key = ""
    preferred_sources: list[str] = []
    cleaned_query = without_memory_flag

    # "explicar X" / "explain X" is our built-in help lane.
    # It should pull from user_spaces.help (not from the LLM).
    forced_help = False
    if cleaned_query == "explicar" or cleaned_query.startswith("explicar "):
        source_key = "help"
        preferred_sources = ["user_spaces.help"]
        cleaned_query = cleaned_query[len("explicar") :].strip()
        forced_help = True
    elif cleaned_query == "explain" or cleaned_query.startswith("explain "):
        source_key = "help"
        preferred_sources = ["user_spaces.help"]
        cleaned_query = cleaned_query[len("explain") :].strip()
        forced_help = True

    if forced_help:
        cleaned_query = _strip_prefixes(normalize_text(cleaned_query))
        cleaned_query = _strip_noise_words(cleaned_query)
        return MemoryQueryIntent(
            cleaned_query=cleaned_query or without_memory_flag,
            hint=TaskContextHint(preferred_sources=preferred_sources),
            source_key=source_key or "help",
        )

    for aliases, source in _SOURCE_PATTERNS:
        for alias in aliases:
            phrase_for = f"{alias} for "
            phrase_in = f"{alias} in "
            if cleaned_query.startswith(phrase_for):
                source_key = alias
                preferred_sources = [source]
                cleaned_query = cleaned_query[len(phrase_for) :].strip()
                break
            if cleaned_query.startswith(phrase_in):
                source_key = alias
                preferred_sources = [source]
                cleaned_query = cleaned_query[len(phrase_in) :].strip()
                break
            if f" {phrase_for}" in cleaned_query:
                source_key = alias
                preferred_sources = [source]
                cleaned_query = cleaned_query.split(phrase_for, 1)[1].strip()
                break
            if f" {phrase_in}" in cleaned_query:
                source_key = alias
                preferred_sources = [source]
                cleaned_query = cleaned_query.split(phrase_in, 1)[1].strip()
                break
            if alias in cleaned_query.split():
                source_key = alias
                preferred_sources = [source]
                cleaned_query = cleaned_query.replace(alias, " ").strip()
                break
        if preferred_sources:
            break

    cleaned_query = _strip_prefixes(normalize_text(cleaned_query))
    cleaned_query = _strip_noise_words(cleaned_query)

    return MemoryQueryIntent(
        cleaned_query=cleaned_query or without_memory_flag,
        hint=TaskContextHint(preferred_sources=preferred_sources),
        source_key=source_key,
    )


def is_persona_lookup_request(text: str, *, flags: dict | None = None) -> bool:
    parsed = parse_memory_query_intent(text)
    if parsed.hint.preferred_sources != ["personas"]:
        return False

    normalized = normalize_text(text)
    flags = flags or {}
    if bool(flags.get("use_memory", False)) or detect_use_memory_flag(normalized):
        return True

    if any(
        normalized.startswith(prefix)
        for prefix in (
            "do we have",
            "is there",
            "check personas",
            "check persona",
            "check profile",
            "check profiles",
            "find persona",
            "find profile",
            "show persona",
            "show profile",
        )
    ):
        return True

    return False
