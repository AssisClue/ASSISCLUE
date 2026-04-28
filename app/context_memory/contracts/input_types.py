from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ChatMessageInput:
    role: str
    text: str
    ts: float | None = None
    message_id: str | None = None
    source: str = "chat_history"


@dataclass(slots=True)
class EventInput:
    event_type: str
    text: str
    ts: float | None = None
    event_id: str | None = None
    source: str = "session_event"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScreenshotNoteInput:
    text: str
    ts: float | None = None
    screenshot_id: str | None = None
    source: str = "screenshot_note"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FileContextInput:
    path: str
    text: str
    ts: float | None = None
    source: str = "file_context"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeStateInput:
    source_name: str
    payload: dict[str, Any]
    ts: float | None = None


@dataclass(slots=True)
class SourceBundleInput:
    chat_messages: list[ChatMessageInput] = field(default_factory=list)
    session_events: list[EventInput] = field(default_factory=list)
    screenshot_notes: list[ScreenshotNoteInput] = field(default_factory=list)
    file_context_items: list[FileContextInput] = field(default_factory=list)
    runtime_states: list[RuntimeStateInput] = field(default_factory=list)