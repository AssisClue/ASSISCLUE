from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

LibraryItemKind = Literal["file"]
LibraryRootKind = Literal["library", "collection"]


@dataclass(slots=True)
class RegisteredRoot:
    root_id: str
    name: str
    path: str
    kind: LibraryRootKind = "library"
    tags: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass(slots=True)
class FileScanRecord:
    root_id: str
    relative_path: str
    absolute_path: str
    file_name: str
    extension: str
    size_bytes: int
    modified_ts: float
    sha1: str
    item_kind: LibraryItemKind = "file"
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    root: RegisteredRoot
    scanned_at: float
    item_count: int
    items: list[FileScanRecord] = field(default_factory=list)