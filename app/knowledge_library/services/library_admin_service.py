from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5

from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.contracts.library_types import RegisteredRoot
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class LibraryAdminService:
    def __init__(self) -> None:
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.store = LibraryMapStore(self.paths.library_roots_path())

    def _load_payload(self) -> list[dict]:
        raw = self.store.load(default=[])
        return raw if isinstance(raw, list) else []

    def _save_payload(self, payload: list[dict]) -> None:
        self.store.save(payload)

    def list_roots(self) -> list[RegisteredRoot]:
        return [RegisteredRoot(**item) for item in self._load_payload() if isinstance(item, dict)]

    def register_root(
        self,
        *,
        name: str,
        path: str,
        kind: str = "library",
        tags: list[str] | None = None,
    ) -> RegisteredRoot:
        clean_name = str(name).strip()
        clean_path = str(path).strip()
        if not clean_name:
            raise ValueError("Root name cannot be empty.")
        if not clean_path:
            raise ValueError("Root path cannot be empty.")

        roots = self._load_payload()
        root_id = str(uuid5(NAMESPACE_URL, f"knowledge-library-root:{clean_name}:{clean_path}:{kind}"))
        new_root = RegisteredRoot(
            root_id=root_id,
            name=clean_name,
            path=clean_path,
            kind=str(kind or "library").strip() or "library",
            tags=[str(tag).strip() for tag in (tags or []) if str(tag).strip()],
            enabled=True,
        )

        filtered = [item for item in roots if str(item.get("root_id", "")).strip() != root_id]
        filtered.append(
            {
                "root_id": new_root.root_id,
                "name": new_root.name,
                "path": new_root.path,
                "kind": new_root.kind,
                "tags": list(new_root.tags),
                "enabled": bool(new_root.enabled),
            }
        )
        self._save_payload(filtered)
        return new_root

    def remove_root(self, root_id: str) -> bool:
        clean_root_id = str(root_id).strip()
        if not clean_root_id:
            return False

        roots = self._load_payload()
        filtered = [item for item in roots if str(item.get("root_id", "")).strip() != clean_root_id]
        changed = len(filtered) != len(roots)
        if changed:
            self._save_payload(filtered)
        return changed