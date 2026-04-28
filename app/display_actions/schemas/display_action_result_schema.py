from __future__ import annotations

from typing import Any, TypedDict


class DisplayActionResult(TypedDict, total=False):
    result_id: str
    ts: float
    ok: bool
    action_name: str
    source_event_id: str
    routed_event_id: str
    screenshot_path: str
    screenshot_created: bool
    used_existing_screenshot: bool
    error_code: str
    analysis_text: str
    speech_text: str
    flags: dict[str, Any]
    meta: dict[str, Any]