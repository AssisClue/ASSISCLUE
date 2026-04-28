from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WebPageIdentity:
    url: str = ""
    title: str = ""


@dataclass(slots=True)
class WebSavedArtifact:
    ok: bool = True
    kind: str = ""
    path: str = ""
    filename: str = ""
    url: str = ""
    title: str = ""
    length: int = 0
    meta: dict[str, Any] = field(default_factory=dict)