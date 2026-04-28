from __future__ import annotations

from typing import Protocol

from .library_types import RegisteredRoot, ScanResult


class LibraryAdminServiceProtocol(Protocol):
    def register_root(
        self,
        *,
        name: str,
        path: str,
        kind: str = "library",
        tags: list[str] | None = None,
    ) -> RegisteredRoot: ...

    def list_roots(self) -> list[RegisteredRoot]: ...

    def remove_root(self, root_id: str) -> bool: ...


class LibraryServiceProtocol(Protocol):
    def scan_all(self) -> dict: ...

    def scan_root(self, root_id: str) -> ScanResult: ...

    def get_library_map(self) -> dict: ...