from __future__ import annotations

import re
from difflib import SequenceMatcher


_PUNCT_RE = re.compile(r"[^a-z0-9\s]")


TOKEN_REPLACEMENTS = {
    "heyy": "hey",
    "heyy": "hey",
    "hay": "hey",
    "ei": "hey",
    "jei": "hey",
    "heigh": "hey",
    "height": "hey",
    "hi": "hey",
    "okey": "ok",
    "okay": "ok",
    "assis": "assistant",
    "assistance": "assistant",
    "assist": "assistant",
    "asistant": "assistant",
    "assistand": "assistant",
    "assistent": "assistant",
    "rickk": "rick",
    "rik": "rick",
    "ric": "rick",
    "rig": "rick",
    "ricky": "rick",
    "henry": "rick",
    "AI": "rick",
}


WAKEWORD_ALIAS_MAP: dict[str, list[str]] = {
    "hey": [
        "hey",
        "ei",
        "a",
        "he",
        "hei",
        "hair",
        "her",
        "ey",
        "ai",
    ],
    "assistant": [
        "assistant",
        "assis",
        "assist",
        "asistant",
        "assistent",
        "assistantt",
    ],
    "rick": [
        "rick",
        "rik",
        "ric",
        "rig",
        "ricky",
        "henry",
        "Hey",
        "ai"


    ],
    "hello assistant": [
        "hello assistant",
        "hello assis",
        "hello asistant",
    ],
    "hey assistant": [
        "hey",
        "hi",
        "hey assis",
    ],
    "ok assistant": [
        "ok assistant",
        "okay assistant",
        "ok assis",
    ],
}


QUESTION_STARTERS = {
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "which",
    "can",
    "could",
    "do",
    "does",
    "did",
    "is",
    "are",
    "was",
    "were",
    "will",
    "would",
}


STRONG_NO_WAKEWORD_PATTERNS = (
    "are you there",
    "what can you do",
    "what model are you using",
    "can you use memory",
    "use memory",
    "analyze last screenshot",
    "analyze screenshot",
    "take screenshot",
    "take a screenshot",
    "take a picture",
)


def normalize_text_strong(text: str) -> str:
    base = (text or "").strip().lower()
    base = _PUNCT_RE.sub(" ", base)
    words = []
    for part in base.split():
        words.append(TOKEN_REPLACEMENTS.get(part, part))
    return " ".join(words).strip()


def fuzzy_token_match(left: str, right: str) -> bool:
    if left == right:
        return True
    if not left or not right:
        return False
    if len(left) <= 2 or len(right) <= 2:
        return False
    return SequenceMatcher(None, left, right).ratio() >= 0.84


def wakeword_candidates(base_wakewords: list[str]) -> list[str]:
    candidates: set[str] = set()
    for wakeword in base_wakewords:
        normalized = normalize_text_strong(wakeword)
        if normalized:
            candidates.add(normalized)
            for alias in WAKEWORD_ALIAS_MAP.get(normalized, []):
                alias_normalized = normalize_text_strong(alias)
                if alias_normalized:
                    candidates.add(alias_normalized)
    return sorted(candidates, key=len, reverse=True)


def phrase_matches_at(words: list[str], start: int, candidate_words: list[str]) -> bool:
    if start + len(candidate_words) > len(words):
        return False
    for idx, cand in enumerate(candidate_words):
        current = words[start + idx]
        if current == cand:
            continue
        if not fuzzy_token_match(current, cand):
            return False
    return True


def looks_like_strong_no_wakeword_question(text: str, *, max_words: int) -> bool:
    normalized = normalize_text_strong(text)
    if not normalized:
        return False

    words = normalized.split()
    if not words or len(words) > max_words:
        return False

    if normalized in STRONG_NO_WAKEWORD_PATTERNS:
        return True

    if any(normalized.startswith(f"{pattern} ") for pattern in STRONG_NO_WAKEWORD_PATTERNS):
        return True

    if words[0] in QUESTION_STARTERS:
        if any(key in normalized for key in ("memory", "model", "screenshot", "screen")):
            return True
        if len(words) <= 6:
            return True

    return False
