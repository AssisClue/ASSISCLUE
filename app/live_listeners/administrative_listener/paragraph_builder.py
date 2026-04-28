from __future__ import annotations

from typing import Any

from app.live_listeners.shared.listener_record_utils import get_record_text

from .administrative_listener_config import MIN_PARAGRAPH_CHARS, MIN_PARAGRAPH_WORDS


def _word_count(text: str) -> int:
    return len([part for part in text.split() if part])


def build_paragraph(records: list[dict[str, Any]]) -> str:
    parts: list[str] = []

    for record in records:
        text = get_record_text(record)
        if not text:
            continue
        parts.append(text)

    paragraph = " ".join(parts).strip()
    paragraph = " ".join(paragraph.split())

    if len(paragraph) < MIN_PARAGRAPH_CHARS:
        return ""

    if _word_count(paragraph) < MIN_PARAGRAPH_WORDS:
        return ""

    return paragraph
