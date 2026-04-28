from __future__ import annotations


def normalize_memory_text(text: str) -> str:
    cleaned = " ".join(text.strip().lower().split())
    for ch in ".,!?;:\"'()[]{}":
        cleaned = cleaned.replace(ch, "")
    return cleaned