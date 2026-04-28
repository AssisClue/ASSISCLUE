from __future__ import annotations

from app.schemas.output_event import OutputEvent


def make_text_output(text: str) -> OutputEvent:
    cleaned = text.strip()
    return OutputEvent(
        output_type="text",
        content=cleaned,
        metadata={"length": len(cleaned)},
    )