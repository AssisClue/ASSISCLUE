from __future__ import annotations


def _normalize_pipeline_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def prepare_tts_text(text: str) -> str:
    cleaned = _normalize_pipeline_text(text)
    if not cleaned:
        return ""
    return cleaned


def should_skip_tts(text: str) -> bool:
    return not bool(prepare_tts_text(text))


def prepare_stt_text(text: str) -> str:
    return _normalize_pipeline_text(text)