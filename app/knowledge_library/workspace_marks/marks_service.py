from __future__ import annotations

from pathlib import Path
import time
from uuid import NAMESPACE_URL, uuid5

from .marks_store import WorkspaceMarksStore
from .marks_types import WorkspaceMark, WorkspaceSection, WorkspaceSourceType


class WorkspaceMarksService:
    def __init__(self, runtime_root: Path | None = None) -> None:
        base = runtime_root or Path("runtime") / "knowledge_library" / "workspace"
        self.runtime_root = Path(base)
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        self.store = WorkspaceMarksStore(self.runtime_root / "marked_items.json")

    def _make_mark_id(
        self,
        *,
        source_type: str,
        section: str,
        path: str,
    ) -> str:
        return str(uuid5(NAMESPACE_URL, f"workspace-mark:{source_type}:{section}:{path}"))

    def _normalize_section(self, section: str) -> WorkspaceSection:
        clean = str(section or "").strip().lower()
        allowed = {
            "library",
            "knowledge_runtime",
            "visual_web",
            "memory_related",
        }
        if clean not in allowed:
            raise ValueError(f"Invalid section: {section}")
        return clean  # type: ignore[return-value]

    def _normalize_source_type(self, source_type: str) -> WorkspaceSourceType:
        clean = str(source_type or "").strip().lower()
        allowed = {
            "library_file",
            "system_file",
        }
        if clean not in allowed:
            raise ValueError(f"Invalid source_type: {source_type}")
        return clean  # type: ignore[return-value]

    def _file_snapshot(self, path: str) -> dict:
        target = Path(str(path or "").strip())
        exists = target.exists() and target.is_file()

        size_bytes = 0
        if exists:
            try:
                size_bytes = int(target.stat().st_size)
            except Exception:
                size_bytes = 0

        return {
            "exists": bool(exists),
            "size_bytes": size_bytes,
            "file_name": target.name if target.name else str(path),
            "extension": target.suffix.lower() if target.suffix else "",
        }

    def _load(self) -> list[dict]:
        return self.store.load()

    def _save(self, payload: list[dict]) -> None:
        self.store.save(payload)

    def list_marks(self) -> list[dict]:
        marks = self._load()
        return sorted(
            marks,
            key=lambda item: float(item.get("updated_at", 0.0) or 0.0),
            reverse=True,
        )

    def get_mark(self, mark_id: str) -> dict | None:
        clean = str(mark_id or "").strip()
        for item in self._load():
            if str(item.get("mark_id", "")).strip() == clean:
                return item
        return None

    def mark_item(
        self,
        *,
        source_type: str,
        section: str,
        file_name: str,
        path: str,
        extension: str = "",
        item_id: str | None = None,
        root_name: str = "",
        sha1: str = "",
        size_bytes: int = 0,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> dict:
        clean_source_type = self._normalize_source_type(source_type)
        clean_section = self._normalize_section(section)
        clean_path = str(path or "").strip()

        if not clean_path:
            raise ValueError("path cannot be empty.")

        snapshot = self._file_snapshot(clean_path)
        mark_id = self._make_mark_id(
            source_type=clean_source_type,
            section=clean_section,
            path=clean_path,
        )
        now = time.time()

        payload = self._load()
        existing = next(
            (item for item in payload if str(item.get("mark_id", "")).strip() == mark_id),
            None,
        )
        filtered = [item for item in payload if str(item.get("mark_id", "")).strip() != mark_id]

        summary_ready = bool((existing or {}).get("summary_ready", False))
        index_ready = bool((existing or {}).get("index_ready", False))
        promoted = bool((existing or {}).get("promoted", False))
        status = str((existing or {}).get("status", "marked") or "marked").strip() or "marked"
        last_error = str((existing or {}).get("last_error", "") or "").strip()

        mark = WorkspaceMark(
            mark_id=mark_id,
            source_type=clean_source_type,
            section=clean_section,
            file_name=str(file_name or snapshot["file_name"]).strip() or snapshot["file_name"],
            path=clean_path,
            extension=str(extension or snapshot["extension"]).strip().lower(),
            item_id=str(item_id).strip() if item_id else None,
            root_name=str(root_name or "").strip(),
            created_at=float((existing or {}).get("created_at", now) or now),
            updated_at=now,
            exists=bool(snapshot["exists"]),
            sha1=str(sha1 or "").strip(),
            size_bytes=int(size_bytes or snapshot["size_bytes"] or 0),
            status=status,
            summary_ready=summary_ready,
            index_ready=index_ready,
            promoted=promoted,
            notes=str(notes or "").strip(),
            tags=[str(tag).strip() for tag in (tags or []) if str(tag).strip()],
            last_error=last_error,
        )

        filtered.append(mark.to_dict())
        self._save(filtered)
        return mark.to_dict()

    def unmark_item(self, mark_id: str) -> bool:
        clean = str(mark_id or "").strip()
        if not clean:
            return False

        payload = self._load()
        filtered = [item for item in payload if str(item.get("mark_id", "")).strip() != clean]
        changed = len(filtered) != len(payload)
        if changed:
            self._save(filtered)
        return changed

    def refresh_mark(self, mark_id: str) -> dict:
        existing = self.get_mark(mark_id)
        if existing is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        return self.mark_item(
            source_type=str(existing.get("source_type", "system_file")),
            section=str(existing.get("section", "library")),
            file_name=str(existing.get("file_name", "")),
            path=str(existing.get("path", "")),
            extension=str(existing.get("extension", "")),
            item_id=str(existing.get("item_id", "")).strip() or None,
            root_name=str(existing.get("root_name", "")),
            sha1=str(existing.get("sha1", "")),
            size_bytes=int(existing.get("size_bytes", 0) or 0),
            notes=str(existing.get("notes", "")),
            tags=list(existing.get("tags", []) or []),
        )

    def update_mark_state(
        self,
        mark_id: str,
        *,
        status: str | None = None,
        summary_ready: bool | None = None,
        index_ready: bool | None = None,
        promoted: bool | None = None,
        notes: str | None = None,
        last_error: str | None = None,
    ) -> dict:
        existing = self.get_mark(mark_id)
        if existing is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        now = time.time()
        updated = dict(existing)
        updated["updated_at"] = now

        if status is not None:
            updated["status"] = str(status).strip() or updated.get("status", "marked")
        if summary_ready is not None:
            updated["summary_ready"] = bool(summary_ready)
        if index_ready is not None:
            updated["index_ready"] = bool(index_ready)
        if promoted is not None:
            updated["promoted"] = bool(promoted)
        if notes is not None:
            updated["notes"] = str(notes)
        if last_error is not None:
            updated["last_error"] = str(last_error)

        payload = self._load()
        filtered = [item for item in payload if str(item.get("mark_id", "")).strip() != str(mark_id).strip()]
        filtered.append(updated)
        self._save(filtered)
        return updated

    def grouped_marks(self) -> dict[str, list[dict]]:
        sections = {
            "library": [],
            "knowledge_runtime": [],
            "visual_web": [],
            "memory_related": [],
        }

        for item in self.list_marks():
            section = str(item.get("section", "")).strip()
            if section in sections:
                sections[section].append(item)

        return sections

    def find_mark_by_path(self, path: str) -> dict | None:
        clean_path = str(path or "").strip()
        if not clean_path:
            return None
        for item in self._load():
            if str(item.get("path", "")).strip() == clean_path:
                return item
        return None