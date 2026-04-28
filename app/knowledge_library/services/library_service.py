from __future__ import annotations

from app.knowledge_library.orchestration.library_scan_pipeline import LibraryScanPipeline
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths
from app.knowledge_library.backends.json.library_map_store import LibraryMapStore

from .library_admin_service import LibraryAdminService


class LibraryService:
    def __init__(self) -> None:
        self.admin = LibraryAdminService()
        self.pipeline = LibraryScanPipeline()
        self.paths = KnowledgeLibraryStoragePaths()
        self.map_store = LibraryMapStore(self.paths.library_map_path())

    def scan_all(self) -> dict:
        roots = self.admin.list_roots()
        return self.pipeline.scan_all(roots=roots)

    def scan_root(self, root_id: str) -> dict:
        roots = self.admin.list_roots()
        target = next((root for root in roots if root.root_id == root_id), None)
        if target is None:
            raise ValueError(f"Unknown root_id: {root_id}")
        result = self.pipeline.scan_root(root=target)
        return {
            "root": {
                "root_id": result.root.root_id,
                "name": result.root.name,
                "path": result.root.path,
                "kind": result.root.kind,
                "tags": list(result.root.tags),
                "enabled": bool(result.root.enabled),
            },
            "scanned_at": result.scanned_at,
            "item_count": result.item_count,
            "items": [item.__dict__ for item in result.items],
        }

    def get_library_map(self) -> dict:
        raw = self.map_store.load(default={})
        return raw if isinstance(raw, dict) else {}