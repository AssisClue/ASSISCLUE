from __future__ import annotations

from typing import Any, TypedDict


class SpokenQueryResult(TypedDict, total=False):
    result_id: str
    ts: float
    ok: bool
    runner_name: str
    source_event_id: str
    routed_event_id: str
    query_text: str
    answer_text: str
    speech_text: str
    error_code: str
    flags: dict[str, Any]
    meta: dict[str, Any]