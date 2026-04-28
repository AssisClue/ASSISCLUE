from __future__ import annotations

import re
import unicodedata


_MOJIBAKE_HINTS = (
    "Ã",
    "Â",
    "â",
    "ðŸ",
    "\ufffd",
)

_DIRECT_REPAIRS = (
    ("Â¿", "\u00bf"),
    ("Â¡", "\u00a1"),
    ("â€™", "'"),
    ("â€˜", "'"),
    ("â€œ", '"'),
    ("â€\x9d", '"'),
    ("â€¦", "..."),
    ("â€“", "-"),
    ("â€”", "-"),
)


def _mojibake_score(text: str) -> int:
    score = 0
    for token in _MOJIBAKE_HINTS:
        score += text.count(token)
    return score


def _repair_once(text: str) -> str:
    best = text
    best_score = _mojibake_score(text)

    for encoding in ("latin-1", "cp1252"):
        try:
            candidate = text.encode(encoding).decode("utf-8")
        except UnicodeError:
            continue
        candidate_score = _mojibake_score(candidate)
        if candidate_score < best_score:
            best = candidate
            best_score = candidate_score

    return best


def repair_common_mojibake(text: str) -> str:
    if not text:
        return ""

    fixed = str(text)
    for _ in range(2):
        next_fixed = _repair_once(fixed)
        if next_fixed == fixed:
            break
        fixed = next_fixed

    for wrong, right in _DIRECT_REPAIRS:
        fixed = fixed.replace(wrong, right)

    return fixed


def normalize_pipeline_text(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text)
    cleaned = unicodedata.normalize("NFC", cleaned)
    cleaned = repair_common_mojibake(cleaned)
    cleaned = unicodedata.normalize("NFC", cleaned)
    cleaned = cleaned.replace("\u00a0", " ")
    cleaned = " ".join(cleaned.strip().split())
    cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"([\u00bf\u00a1])\s+", r"\1", cleaned)
    return cleaned.strip()
