from __future__ import annotations

from .primary_listener_config import DEFAULT_WAKEWORDS
from .matcher_vocabulary import (
    normalize_text_strong,
    phrase_matches_at,
    wakeword_candidates,
)


def normalize_text(text: str) -> str:
    return normalize_text_strong(text)


def _sorted_wakewords(wakewords: list[str] | None = None) -> list[str]:
    active_wakewords = wakewords or DEFAULT_WAKEWORDS
    return wakeword_candidates(active_wakewords)


def has_wakeword(text: str, wakewords: list[str] | None = None) -> bool:
    return bool(find_matched_wakeword(text, wakewords=wakewords))


def find_matched_wakeword(text: str, wakewords: list[str] | None = None) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return ""

    words = normalized.split()
    restricted_mid_sentence = {"hey", "a", "he", "her", "ey", "ei", "ai", "hei", "hair"}
    for candidate in _sorted_wakewords(wakewords):
        candidate_words = candidate.split()
        candidate_len = len(candidate_words)
        if candidate_len == 0 or candidate_len > len(words):
            continue

        for start_index in range(0, len(words) - candidate_len + 1):
            if candidate in restricted_mid_sentence and start_index != 0:
                continue
            if phrase_matches_at(words, start_index, candidate_words):
                return candidate

    return ""


def split_after_wakeword(text: str, wakewords: list[str] | None = None) -> tuple[str, str]:
    normalized = normalize_text(text)
    if not normalized:
        return "", ""

    matched = find_matched_wakeword(normalized, wakewords=wakewords)
    if not matched:
        return "", normalized

    words = normalized.split()
    matched_words = matched.split()
    for start_index in range(0, len(words) - len(matched_words) + 1):
        if phrase_matches_at(words, start_index, matched_words):
            tail_words = words[start_index + len(matched_words) :]
            return matched, " ".join(tail_words).strip()

    return matched, ""


def strip_wakeword_prefix(text: str, wakewords: list[str] | None = None) -> str:
    _, tail_text = split_after_wakeword(text, wakewords=wakewords)
    return tail_text
