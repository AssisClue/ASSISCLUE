from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class UserSpaceItem:
    item_id: str
    space_id: str
    title: str = ""
    text: str = ""
    tags: list[str] = field(default_factory=list)
    ts: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

