from __future__ import annotations

import re


def normalize_llm_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def _split_sentences(text: str) -> list[str]:
    cleaned = normalize_llm_text(text)
    if not cleaned:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def trim_for_ui(text: str, max_chars: int = 220) -> str:
    cleaned = normalize_llm_text(text)
    if len(cleaned) <= max_chars:
        return cleaned

    shortened = cleaned[:max_chars].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0].strip()
    return shortened.rstrip(" ,;:-") + "..."


def trim_for_tts(text: str, max_chars: int = 180) -> str:
    cleaned = normalize_llm_text(text)
    if not cleaned:
        return ""

    sentences = _split_sentences(cleaned)
    candidate = sentences[0] if sentences else cleaned

    if len(candidate) <= max_chars:
        return candidate

    shortened = candidate[:max_chars].rstrip()
    if " " in shortened:
        shortened = shortened.rsplit(" ", 1)[0].strip()
    return shortened.rstrip(" ,;:-") + "..."