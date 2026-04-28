from __future__ import annotations

import inspect
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from app.context_memory.backends.json.json_memory_store import JsonMemoryStore
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.runtime.storage_paths import ContextMemoryStoragePaths


class ContextMemoryBridge:
    def __init__(self) -> None:
        self.paths = ContextMemoryStoragePaths(runtime_root=Path("runtime"))
        self.paths.ensure_directories()
        self.store = JsonMemoryStore(storage_path=self.paths.memory_items_path)

    def _item_signature_fields(self) -> set[str]:
        try:
            return set(inspect.signature(MemoryItem).parameters.keys())
        except Exception:
            return set()

    def _make_item_id(self, source_path: str, chunk_index: int) -> str:
        return str(uuid5(NAMESPACE_URL, f"knowledge-library-promotion:{source_path}:{chunk_index}"))

    def _build_memory_item(
        self,
        *,
        item_id: str,
        text: str,
        source: str,
        kind: str,
        ts: float,
        tags: list[str],
        metadata: dict[str, Any],
        importance: float = 0.6,
    ) -> Any:
        allowed = self._item_signature_fields()

        payload: dict[str, Any] = {
            "item_id": item_id,
            "text": text,
            "kind": kind,
            "source": source,
            "ts": ts,
            "importance": importance,
            "tags": tags,
            "metadata": metadata,
            "project_name": str(metadata.get("project_name", "") or "").strip(),
        }

        if allowed:
            payload = {k: v for k, v in payload.items() if k in allowed}

        return MemoryItem(**payload)

    def _serialize_item(self, item: Any) -> dict[str, Any]:
        if is_dataclass(item):
            return asdict(item)
        if hasattr(item, "to_dict") and callable(item.to_dict):
            return dict(item.to_dict())
        if hasattr(item, "__dict__"):
            return dict(item.__dict__)
        raise TypeError("Unsupported MemoryItem serialization shape.")

    def _load_existing(self) -> list[Any]:
        try:
            return list(self.store.load_memory_items() or [])
        except Exception:
            return []

    def _save_all(self, items: list[Any]) -> None:
        if hasattr(self.store, "save_memory_items"):
            self.store.save_memory_items(items)
            return
        raise AttributeError("JsonMemoryStore does not expose save_memory_items().")

    def _dedupe_keep_latest(self, items: list[Any]) -> list[Any]:
        by_id: dict[str, Any] = {}
        for item in items:
            item_id = ""
            if hasattr(item, "item_id"):
                item_id = str(getattr(item, "item_id", "") or "").strip()
            elif isinstance(item, dict):
                item_id = str(item.get("item_id", "") or "").strip()
            if not item_id:
                continue
            by_id[item_id] = item
        return list(by_id.values())

    def promote_chunks(
        self,
        *,
        source_path: str,
        file_name: str,
        chunks: list[dict],
        summary_text: str | None = None,
        root_name: str = "",
        tags: list[str] | None = None,
        project_name: str = "knowledge_library",
    ) -> dict:
        ts = time.time()
        clean_tags = [str(tag).strip() for tag in (tags or []) if str(tag).strip()]
        new_items: list[Any] = []

        for chunk in chunks:
            chunk_index = int(chunk.get("chunk_index", 0))
            chunk_text = str(chunk.get("text", "") or "").strip()
            if not chunk_text:
                continue

            metadata = {
                "project_name": project_name,
                "library_root_name": root_name,
                "file_name": file_name,
                "source_path": source_path,
                "chunk_index": chunk_index,
                "chunk_start": chunk.get("start_index"),
                "chunk_end": chunk.get("end_index"),
                "tags": list(clean_tags),
                "ingest_source": "knowledge_library",
                "content_kind": "file_chunk",
            }
            new_items.append(
                self._build_memory_item(
                    item_id=self._make_item_id(source_path, chunk_index),
                    text=chunk_text,
                    source="knowledge_library.file",
                    kind="project_context",
                    ts=ts,
                    importance=0.6,
                    tags=clean_tags,
                    metadata=metadata,
                )
            )

        if summary_text:
            summary_clean = str(summary_text).strip()
            if summary_clean:
                metadata = {
                    "project_name": project_name,
                    "library_root_name": root_name,
                    "file_name": file_name,
                    "source_path": source_path,
                    "tags": list(clean_tags),
                    "ingest_source": "knowledge_library",
                    "content_kind": "file_summary",
                }
                new_items.append(
                    self._build_memory_item(
                        item_id=self._make_item_id(source_path, 999999),
                        text=summary_clean,
                        source="knowledge_library.summary",
                        kind="project_context",
                        ts=ts,
                        importance=0.72,
                        tags=clean_tags,
                        metadata=metadata,
                    )
                )

        existing = self._load_existing()
        merged = self._dedupe_keep_latest(existing + new_items)
        self._save_all(merged)

        return {
            "ok": True,
            "promoted_count": len(new_items),
            "source_path": source_path,
            "file_name": file_name,
            "context_memory_backend": "json",
            "memory_items_total": len(merged),
            "promoted_item_ids": [
                self._serialize_item(item).get("item_id", "")
                for item in new_items
            ],
        }