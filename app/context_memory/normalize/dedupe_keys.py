from __future__ import annotations

from app.context_memory.normalize.memory_text_normalizer import normalize_memory_text


def build_dedupe_key(text: str, source: str = "", kind: str = "") -> str:
    normalized_text = normalize_memory_text(text)
    normalized_source = normalize_memory_text(source)
    normalized_kind = normalize_memory_text(kind)
    return f"{normalized_kind}|{normalized_source}|{normalized_text}"