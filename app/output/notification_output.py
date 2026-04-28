from __future__ import annotations

from app.schemas.output_event import OutputEvent


def make_notification_output(text: str) -> OutputEvent:
    cleaned = text.strip()
    return OutputEvent(
        output_type="notification",
        content=cleaned,
        metadata={"level": "info"},
    )