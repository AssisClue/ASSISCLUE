from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.contracts.input_types import (
    ChatMessageInput,
    EventInput,
    FileContextInput,
    RuntimeStateInput,
    ScreenshotNoteInput,
    SourceBundleInput,
)


@dataclass(slots=True)
class InputAssembler:
    chat_messages: list[ChatMessageInput] = field(default_factory=list)
    session_events: list[EventInput] = field(default_factory=list)
    screenshot_notes: list[ScreenshotNoteInput] = field(default_factory=list)
    file_context_items: list[FileContextInput] = field(default_factory=list)
    runtime_states: list[RuntimeStateInput] = field(default_factory=list)

    def build_bundle(self) -> SourceBundleInput:
        return SourceBundleInput(
            chat_messages=list(self.chat_messages),
            session_events=list(self.session_events),
            screenshot_notes=list(self.screenshot_notes),
            file_context_items=list(self.file_context_items),
            runtime_states=list(self.runtime_states),
        )

    def add_chat_messages(self, items: list[ChatMessageInput]) -> None:
        self.chat_messages.extend(items)

    def add_session_events(self, items: list[EventInput]) -> None:
        self.session_events.extend(items)

    def add_screenshot_notes(self, items: list[ScreenshotNoteInput]) -> None:
        self.screenshot_notes.extend(items)

    def add_file_context_items(self, items: list[FileContextInput]) -> None:
        self.file_context_items.extend(items)

    def add_runtime_states(self, items: list[RuntimeStateInput]) -> None:
        self.runtime_states.extend(items)

    def clear(self) -> None:
        self.chat_messages.clear()
        self.session_events.clear()
        self.screenshot_notes.clear()
        self.file_context_items.clear()
        self.runtime_states.clear()