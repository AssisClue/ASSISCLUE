from __future__ import annotations

import time

from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.contracts.library_types import RegisteredRoot, ScanResult
from app.knowledge_library.library_map.file_registry import FileRegistry
from app.knowledge_library.library_map.folder_scanner import FolderScanner
from app.knowledge_library.library_map.library_map_builder import LibraryMapBuilder
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class LibraryScanPipeline:
    def __init__(self) -> None:
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.map_store = LibraryMapStore(self.paths.library_map_path())
        self.hash_store = LibraryMapStore(self.paths.file_hash_index_path())
        self.status_store = LibraryMapStore(self.paths.scan_status_path())
        self.scanner = FolderScanner()
        self.registry = FileRegistry()

    def _build_hash_index(self, items: list[dict]) -> dict:
        return {
            item["item_id"]: {
                "sha1": item["sha1"],
                "relative_path": item["relative_path"],
                "root_id": item["root_id"],
            }
            for item in items
        }

    def scan_all(self, roots: list[RegisteredRoot]) -> dict:
        builder = LibraryMapBuilder(scanner=self.scanner, registry=self.registry)
        library_map = builder.build(roots=roots)
        payload = library_map.to_dict()

        self.map_store.save(payload)
        self.hash_store.save(self._build_hash_index(payload["items"]))
        self.status_store.save(
            {
                "ok": True,
                "last_scan_ts": payload["generated_at"],
                "root_count": payload["root_count"],
                "item_count": payload["item_count"],
            }
        )
        return payload

    def scan_root(self, root: RegisteredRoot) -> ScanResult:
        items = []
        for file_path in self.scanner.iter_files(root_path=__import__("pathlib").Path(root.path)):
            items.append(self.registry.build_record(root=root, file_path=file_path))

        return ScanResult(
            root=root,
            scanned_at=time.time(),
            item_count=len(items),
            items=items,
        )