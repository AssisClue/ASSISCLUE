from __future__ import annotations

import json
from pathlib import Path

from app.knowledge_library.backends.context_bridge.context_memory_bridge import ContextMemoryBridge
from app.knowledge_library.backends.context_bridge.qdrant_bridge import QdrantBridge
from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class PromoteToContextPipeline:
    def __init__(self) -> None:
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.map_store = LibraryMapStore(self.paths.library_map_path())
        self.context_bridge = ContextMemoryBridge()
        self.qdrant_bridge = QdrantBridge()

    def _resolve_item(self, item_id: str) -> dict:
        raw = self.map_store.load(default={})
        items = raw.get("items", []) if isinstance(raw, dict) else []
        for item in items:
            if str(item.get("item_id", "")).strip() == str(item_id).strip():
                return item
        raise ValueError(f"Unknown item_id: {item_id}")

    def _manifest_path(self, item_id: str) -> Path:
        return self.paths.runtime_root() / "indexing" / "chunk_manifests" / f"{item_id}.json"

    def _load_chunks(self, item_id: str) -> list[dict]:
        path = self._manifest_path(item_id)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Chunk manifest not found: {path}")
        raw = json.loads(path.read_text(encoding="utf-8"))
        chunks = raw.get("chunks", []) if isinstance(raw, dict) else []
        return chunks if isinstance(chunks, list) else []

    def _load_latest_summary_for_item(self, item_id: str) -> str:
        summaries_path = self.paths.runtime_root() / "summaries" / "book_summaries.jsonl"
        if not summaries_path.exists() or not summaries_path.is_file():
            return ""

        latest = ""
        for line in summaries_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if str(payload.get("item_id", "")).strip() == str(item_id).strip():
                latest = str(payload.get("summary_text", "") or "").strip()
        return latest

    def promote(
        self,
        *,
        item_id: str,
        rebuild_qdrant: bool = False,
    ) -> dict:
        item = self._resolve_item(item_id)
        chunks = self._load_chunks(item_id)
        summary_text = self._load_latest_summary_for_item(item_id)

        promoted = self.context_bridge.promote_chunks(
            source_path=str(item["absolute_path"]),
            file_name=str(item["file_name"]),
            chunks=chunks,
            summary_text=summary_text,
            root_name=str(item.get("root_name", "") or "").strip(),
            tags=list(item.get("tags", []) or []),
            project_name="knowledge_library",
        )

        qdrant_result = {
            "ok": True,
            "status": "skipped",
        }
        if rebuild_qdrant:
            qdrant_result = self.qdrant_bridge.rebuild_from_context_memory_json()

        return {
            "ok": True,
            "item_id": str(item["item_id"]),
            "source_path": str(item["absolute_path"]),
            "file_name": str(item["file_name"]),
            "promoted": promoted,
            "qdrant": qdrant_result,
        }
    