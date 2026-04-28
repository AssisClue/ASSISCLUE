from __future__ import annotations

from .primary_listener_config import QUICK_QUESTION_MAX_WORDS, SPOKEN_QUESTION_MAX_WORDS
from .wakeword_matcher import normalize_text


QUESTION_STARTERS = {
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "which",
    "ask",
    "rick",
    "use",
    "think",
    "can",
    "could",
    "did",
    "do",
    "does",
    "is",
    "are",
    "was",
    "were",
}

SPOKEN_QUESTION_PREFIXES = (
    "can you",
    "could you",
    "would you",
    "do you know",
    "tell me",
    "explain",
    "help me understand",
    "what do you think",
    "why did",
    "how come",
)

SPOKEN_QUESTION_MARKERS = {
    "why",
    "how",
    "what",
    "when",
    "where",
    "who",
    "which",
    "explain",
}

_LEADING_FILLER_WORDS = {
    "wait",
    "yeah",
    "please",
    "well",
    "so",
    "um",
    "uh",
    "just",
    "like",
}

_POLITE_PREFIXES = (
    "i want you to",
    "i need you to",
    "i would like you to",
)

_REQUEST_STARTERS = {
    "show",
    "tell",
    "explain",
    "help",
    "give",
    "provide",
    "summarize",
    "say",
    "open",
    "close",
    "turn",
    "repeat",
    "pause",
    "resume",
    "stop",
    "start",
    "check",
    "look",
    "search",
    "find",
    "list",
    "review",
    "compare",
    "read",
    "analyze",
}

_REQUEST_PREFIXES = (
    "look up",
    "look in",
    "search for",
    "find",
    "find me",
    "check for",
    "tell me",
    "show me",
    "help me",
)


def _word_count(text: str) -> int:
    return len([part for part in text.split() if part])


def _strip_leading_fillers(normalized: str, *, max_words: int = 3) -> str:
    words = [part for part in str(normalized or "").split() if part]
    removed = 0
    while words and removed < max_words and words[0] in _LEADING_FILLER_WORDS:
        words = words[1:]
        removed += 1
    return " ".join(words).strip()


def _strip_polite_prefixes(normalized: str) -> str:
    cleaned = str(normalized or "").strip()
    for prefix in _POLITE_PREFIXES:
        if cleaned == prefix or cleaned.startswith(prefix + " "):
            return cleaned[len(prefix):].strip()
    return cleaned


def _normalize_for_intent(text: str) -> str:
    normalized = normalize_text(text)
    normalized = _strip_leading_fillers(normalized)
    normalized = _strip_polite_prefixes(normalized)
    normalized = _strip_leading_fillers(normalized)
    return normalized


def looks_like_quick_question(text: str) -> bool:
    normalized = _normalize_for_intent(text)
    if not normalized:
        return False

    if _word_count(normalized) > QUICK_QUESTION_MAX_WORDS:
        return False

    first_word = normalized.split()[0]
    if first_word in QUESTION_STARTERS:
        return True

    if first_word in _REQUEST_STARTERS:
        return True

    return False


def looks_like_spoken_question(text: str) -> bool:
    normalized = _normalize_for_intent(text)
    if not normalized:
        return False

    words = normalized.split()
    if len(words) <= QUICK_QUESTION_MAX_WORDS:
        return False

    if len(words) > SPOKEN_QUESTION_MAX_WORDS:
        return False

    if any(normalized.startswith(prefix) for prefix in SPOKEN_QUESTION_PREFIXES):
        return True

    marker_hits = sum(1 for marker in SPOKEN_QUESTION_MARKERS if marker in words)
    if marker_hits >= 2:
        return True

    return False


def looks_like_useful_request(text: str) -> bool:
    normalized = _normalize_for_intent(text)
    if not normalized:
        return False

    words = normalized.split()
    if len(words) < 2 or len(words) > SPOKEN_QUESTION_MAX_WORDS:
        return False

    if any(normalized.startswith(prefix) for prefix in _REQUEST_PREFIXES):
        return True

    first_word = words[0]
    if first_word in _REQUEST_STARTERS and len(words) >= 3:
        return True

    return False
