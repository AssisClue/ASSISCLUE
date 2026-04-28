from __future__ import annotations

from app.schemas.output_event import OutputEvent


def make_image_output(description: str) -> OutputEvent:
    cleaned = description.strip()
    return OutputEvent(
        output_type="image",
        content=cleaned,
        metadata={"kind": "placeholder"},
    )