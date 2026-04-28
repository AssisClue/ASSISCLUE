from __future__ import annotations

from typing import Any, TypedDict


class CommandPayload(TypedDict, total=False):
    command_id: str
    action_name: str
    matched_alias: str
    requires_wakeword: bool
    allow_without_wakeword: bool


class IncomingListenerEvent(TypedDict, total=False):
    event_id: str
    ts: float
    source: str
    event_type: str
    text: str
    original_text: str
    transcript_text: str
    cleaned_text: str
    matched_wakeword: str
    flags: dict[str, Any]
    command: CommandPayload
    routing_hint: str
