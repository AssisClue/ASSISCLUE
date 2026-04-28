from __future__ import annotations

import json

from .common import BaseUiService


class LibraryFileViewService(BaseUiService):
    def get_item_by_id(self, item_id: str) -> dict:
        library_map = self.facade.get_library_map()
        items = library_map.get("items", []) if isinstance(library_map, dict) else []
        target = next((item for item in items if str(item.get("item_id", "")).strip() == str(item_id).strip()), None)
        if target is None:
            raise ValueError(f"Unknown item_id: {item_id}")
        return target

    def is_promoted_item(self, item_id: str) -> bool:
        path = self.project_root() / "runtime" / "memory" / "memory_items.json"
        if not path.exists() or not path.is_file():
            return False

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False

        items = payload if isinstance(payload, list) else payload.get("items", []) if isinstance(payload, dict) else []
        if not isinstance(items, list):
            return False

        target_item = self.get_item_by_id(item_id)
        target_source_path = str(target_item.get("absolute_path", "")).strip()

        for item in items:
            if not isinstance(item, dict):
                continue
            metadata = item.get("metadata", {}) if isinstance(item.get("metadata", {}), dict) else {}
            source_path = str(metadata.get("source_path", "")).strip()
            ingest_source = str(metadata.get("ingest_source", "")).strip()
            if ingest_source == "knowledge_library" and source_path and source_path == target_source_path:
                return True
        return False

    def get_file_payload(self, item_id: str) -> dict:
        target = self.get_item_by_id(item_id)
        preview = self.facade.read_file(item_id=item_id, max_chars=6000)
        summary = self.read_latest_summary_for_item(item_id)
        index_status = self.read_index_status_for_item(item_id)
        promoted = self.is_promoted_item(item_id)

        return {
            "item": target,
            "preview": preview,
            "summary": summary,
            "index_status": index_status,
            "promoted": promoted,
        }