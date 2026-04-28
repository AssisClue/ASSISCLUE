from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContextKind(str, Enum):
    LIVE = "live"
    RECENT = "recent"
    PROFILE = "profile"
    PROJECT = "project"
    TASK = "task"


@dataclass(slots=True)
class ContextSnapshotMetadata:
    kind: ContextKind
    ts: float
    source_count: int = 0
    item_count: int = 0
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)