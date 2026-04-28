from __future__ import annotations

import time

from app.knowledge_library.contracts.library_types import RegisteredRoot
from app.knowledge_library.models.library_item import LibraryItem
from app.knowledge_library.models.library_map import LibraryMap

from .file_registry import FileRegistry
from .folder_scanner import FolderScanner


class LibraryMapBuilder:
    def __init__(
        self,
        scanner: FolderScanner | None = None,
        registry: FileRegistry | None = None,
    ) -> None:
        self.scanner = scanner or FolderScanner()
        self.registry = registry or FileRegistry()

    def build(self, roots: list[RegisteredRoot]) -> LibraryMap:
        items: list[dict] = []

        for root in roots:
            if not root.enabled:
                continue

            for file_path in self.scanner.iter_files(root_path=__import__("pathlib").Path(root.path)):
                record = self.registry.build_record(root=root, file_path=file_path)
                item = LibraryItem(
                    item_id=self.registry.build_item_id(root.root_id, record.relative_path),
                    root_id=root.root_id,
                    root_name=root.name,
                    relative_path=record.relative_path,
                    absolute_path=record.absolute_path,
                    file_name=record.file_name,
                    extension=record.extension,
                    size_bytes=record.size_bytes,
                    modified_ts=record.modified_ts,
                    sha1=record.sha1,
                    tags=list(record.tags),
                    status="mapped",
                )
                items.append(item.to_dict())

        root_payloads = [
            {
                "root_id": root.root_id,
                "name": root.name,
                "path": root.path,
                "kind": root.kind,
                "tags": list(root.tags),
                "enabled": bool(root.enabled),
            }
            for root in roots
        ]

        return LibraryMap(
            generated_at=time.time(),
            root_count=len(root_payloads),
            item_count=len(items),
            roots=root_payloads,
            items=items,
        )