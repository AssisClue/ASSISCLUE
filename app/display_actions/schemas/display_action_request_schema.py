from __future__ import annotations

from typing import Any, TypedDict


class DisplayActionRequest(TypedDict, total=False):
    routed_event_id: str
    ts: float
    source_event_id: str
    source: str
    event_type: str
    target_queue: str
    target_runner: str
    transcript_text: str
    cleaned_text: str
    matched_wakeword: str
    flags: dict[str, Any]
    command: dict[str, Any]
    routing_reason: str