from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import UserSpaceItem
from .storage_paths import UserSpacesStoragePaths, _clean_space_id


class JsonUserSpaceStore:
    def __init__(self, storage_paths: UserSpacesStoragePaths) -> None:
        self._paths = storage_paths
        self._paths.ensure_directories()

    def list_spaces(self) -> list[str]:
        self._paths.ensure_directories()
        spaces: list[str] = []
        for path in self._paths.user_spaces_dir.glob("*.json"):
            name = path.stem.strip()
            if name:
                spaces.append(name)
        for path in self._paths.user_spaces_dir.iterdir():
            if path.is_dir():
                name = path.name.strip()
                if name:
                    spaces.append(name)
        return sorted(set(spaces))

    def load_space(self, space_id: str) -> list[UserSpaceItem]:
        cleaned_space = _clean_space_id(space_id)
        root_items: list[UserSpaceItem] = []

        root_path = self._paths.space_path(cleaned_space)
        if root_path.exists():
            root_items.extend(self._load_space_file(root_path, cleaned_space))

        merged_dir = self._paths.user_spaces_dir / cleaned_space
        if merged_dir.exists() and merged_dir.is_dir():
            for child in sorted(merged_dir.glob("*.json")):
                root_items.extend(self._load_space_file(child, cleaned_space))

        seen: set[str] = set()
        merged: list[UserSpaceItem] = []
        for item in root_items:
            if not item.item_id or item.item_id in seen:
                continue
            seen.add(item.item_id)
            merged.append(item)
        return merged

    def _load_space_file(self, path: Path, cleaned_space: str) -> list[UserSpaceItem]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

        if isinstance(payload, dict) and isinstance(payload.get("items"), list):
            payload = payload["items"]
        if not isinstance(payload, list):
            return []

        items: list[UserSpaceItem] = []
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            item_id = str(raw.get("item_id", "")).strip()
            text = str(raw.get("text", "")).strip()
            if not item_id or not text:
                continue
            tags = raw.get("tags", [])
            items.append(
                UserSpaceItem(
                    item_id=item_id,
                    space_id=str(raw.get("space_id", cleaned_space)).strip() or cleaned_space,
                    title=str(raw.get("title", "")).strip(),
                    text=text,
                    tags=[str(t).strip() for t in tags] if isinstance(tags, list) else [],
                    ts=float(raw.get("ts")) if isinstance(raw.get("ts"), (int, float)) else None,
                    metadata=raw.get("metadata", {}) if isinstance(raw.get("metadata", {}), dict) else {},
                )
            )
        return items

    def save_space(self, space_id: str, items: list[UserSpaceItem]) -> None:
        path = self._paths.space_path(space_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(item) for item in items]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def upsert_item(
        self,
        *,
        space_id: str,
        text: str,
        title: str = "",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        item_id: str = "",
    ) -> UserSpaceItem:
        cleaned_space = _clean_space_id(space_id)
        cleaned_text = str(text or "").strip()
        if not cleaned_text:
            raise ValueError("UserSpaceItem text is empty.")

        items = self.load_space(cleaned_space)
        target_id = str(item_id or "").strip() or f"usit_{uuid4().hex}"

        now = time.time()
        updated = UserSpaceItem(
            item_id=target_id,
            space_id=cleaned_space,
            title=str(title or "").strip(),
            text=cleaned_text,
            tags=[str(t).strip() for t in (tags or []) if str(t).strip()],
            ts=now,
            metadata=dict(metadata or {}),
        )

        replaced = False
        for idx, existing in enumerate(items):
            if existing.item_id == target_id:
                items[idx] = updated
                replaced = True
                break
        if not replaced:
            items.append(updated)

        self.save_space(cleaned_space, items)
        return updated

    def delete_item(self, *, space_id: str, item_id: str) -> bool:
        cleaned_space = _clean_space_id(space_id)
        target_id = str(item_id or "").strip()
        if not target_id:
            return False
        items = self.load_space(cleaned_space)
        remaining = [item for item in items if item.item_id != target_id]
        if len(remaining) == len(items):
            return False
        self.save_space(cleaned_space, remaining)
        return True
