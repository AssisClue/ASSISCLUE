from __future__ import annotations

from typing import Any


def get_record_text(record: dict[str, Any]) -> str:
    return " ".join(str(record.get("text", "")).strip().split())


def get_record_event_id(record: dict[str, Any]) -> str:
    return str(record.get("event_id", "")).strip()


def get_record_ts(record: dict[str, Any]) -> float | None:
    value = record.get("ts")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def get_record_session_id(record: dict[str, Any]) -> str:
    return str(record.get("session_id", "")).strip()


def is_minimal_transcript_record(record: dict[str, Any]) -> bool:
    if not isinstance(record, dict):
        return False

    event_id = get_record_event_id(record)
    text = get_record_text(record)

    return bool(event_id and text)


def same_event(record: dict[str, Any], event_id: str) -> bool:
    return get_record_event_id(record) == str(event_id).strip()