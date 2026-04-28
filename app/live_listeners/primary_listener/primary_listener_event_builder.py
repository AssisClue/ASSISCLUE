from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from .primary_listener_config import (
    EVENT_TYPE_COMMAND,
    EVENT_TYPE_QUICK_QUESTION,
    EVENT_TYPE_WAKEWORD_ONLY,
)


def _base_event(
    record: dict[str, Any],
    *,
    matched_wakeword: str,
    text: str,
    flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_id": f"pevt_{uuid4().hex}",
        "ts": time.time(),
        "source_event_id": record.get("event_id", ""),
        "source_session_id": record.get("session_id", ""),
        "source": "primary_listener",
        "event_type": "",
        "text": text,
        "original_text": record.get("text", ""),
        "transcript_text": record.get("text", ""),
        "cleaned_text": text,
        "matched_wakeword": matched_wakeword,
        "flags": flags if isinstance(flags, dict) else {},
    }


def build_command_event(
    record: dict[str, Any],
    *,
    matched_wakeword: str,
    text: str,
    command_match: dict[str, Any],
    flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = _base_event(
        record,
        matched_wakeword=matched_wakeword,
        text=text,
        flags=flags,
    )
    event["event_type"] = EVENT_TYPE_COMMAND
    event["command"] = command_match
    return event


def build_quick_question_event(
    record: dict[str, Any],
    *,
    matched_wakeword: str,
    text: str,
    flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = _base_event(
        record,
        matched_wakeword=matched_wakeword,
        text=text,
        flags=flags,
    )
    event["event_type"] = EVENT_TYPE_QUICK_QUESTION
    return event


def build_wakeword_only_event(
    record: dict[str, Any],
    *,
    matched_wakeword: str,
    text: str,
    flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event = _base_event(
        record,
        matched_wakeword=matched_wakeword,
        text=text,
        flags=flags,
    )
    event["event_type"] = EVENT_TYPE_WAKEWORD_ONLY
    return event
