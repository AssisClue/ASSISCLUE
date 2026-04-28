from __future__ import annotations

from dataclasses import asdict, dataclass, field
import time
from typing import Literal


WorkspaceSection = Literal[
    "library",
    "knowledge_runtime",
    "visual_web",
    "memory_related",
]

WorkspaceSourceType = Literal[
    "library_file",
    "system_file",
]


@dataclass(slots=True)
class WorkspaceMark:
    mark_id: str
    source_type: WorkspaceSourceType
    section: WorkspaceSection

    file_name: str
    path: str
    extension: str = ""

    item_id: str | None = None
    root_name: str = ""

    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    exists: bool = True
    sha1: str = ""
    size_bytes: int = 0

    status: str = "marked"

    summary_ready: bool = False
    index_ready: bool = False
    promoted: bool = False

    notes: str = ""
    tags: list[str] = field(default_factory=list)
    last_error: str = ""

    def to_dict(self) -> dict:
        return asdict(self)