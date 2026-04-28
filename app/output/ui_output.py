from __future__ import annotations

from app.schemas.output_event import OutputEvent


def make_ui_output(text: str) -> OutputEvent:
    cleaned = text.strip()
    return OutputEvent(
        output_type="ui",
        content=cleaned,
        metadata={"render_target": "chat_panel"},
    )