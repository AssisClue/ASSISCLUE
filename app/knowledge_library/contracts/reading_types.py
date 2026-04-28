from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReadRequest:
    item_id: str | None = None
    absolute_path: str | None = None
    max_chars: int | None = None


@dataclass(slots=True)
class ChapterRequest:
    item_id: str | None = None
    absolute_path: str | None = None
    chapter_number: int | None = None
    chapter_title_hint: str | None = None
    max_chars: int | None = None


@dataclass(slots=True)
class ParagraphSearchRequest:
    item_id: str | None = None
    absolute_path: str | None = None
    query: str = ""
    limit: int = 3
    max_chars_per_result: int = 500


@dataclass(slots=True)
class ReadResult:
    ok: bool
    source_path: str
    file_name: str
    extension: str
    text: str
    text_length: int
    metadata: dict = field(default_factory=dict)