from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RetrievalMode(str, Enum):
    LEXICAL = "lexical"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(slots=True)
class RetrievalFilters:
    kinds: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    project_names: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    min_ts: float | None = None
    max_ts: float | None = None
    limit: int = 8


@dataclass(slots=True)
class RetrievalQuery:
    text: str
    mode: RetrievalMode = RetrievalMode.HYBRID
    filters: RetrievalFilters = field(default_factory=RetrievalFilters)
    hints: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievalResult:
    item_id: str
    text: str
    score: float
    kind: str
    source: str
    ts: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)