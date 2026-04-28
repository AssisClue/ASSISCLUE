from __future__ import annotations

from typing import Any, TypedDict


class SpeechQueueItem(TypedDict, total=False):
    speech_id: str
    ts: float
    source_type: str
    source_event_id: str
    source_result_id: str
    text: str
    spoken_text: str
    priority: str
    flags: dict[str, Any]
    meta: dict[str, Any]