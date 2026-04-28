from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SummarizeRequest:
    item_id: str | None = None
    absolute_path: str | None = None
    max_chars: int = 12000
    max_summary_chars: int = 800


@dataclass(slots=True)
class IndexRequest:
    item_id: str | None = None
    absolute_path: str | None = None
    chunk_size: int = 800
    chunk_overlap: int = 120
    write_vectors: bool = False
    make_summary: bool = True


@dataclass(slots=True)
class IndexResult:
    ok: bool
    source_path: str
    file_name: str
    chunk_count: int
    summary_created: bool
    manifests: dict = field(default_factory=dict)