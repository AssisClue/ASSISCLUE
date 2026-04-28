from __future__ import annotations

import os

from app.knowledge_library.services.knowledge_library_facade import KnowledgeLibraryFacade
from app.knowledge_library.workspace_marks.marks_service import WorkspaceMarksService


class WorkspaceUiService:
    BOX_ORDER = [
        ("marked", "MARKED"),
        ("summarized", "SUMMARIZED"),
        ("indexed", "INDEXED"),
        ("promoted", "PROMOTED"),
    ]

    def __init__(self) -> None:
        self.marks = WorkspaceMarksService()
        self.facade = KnowledgeLibraryFacade()

    def _open_url_for_mark(self, item: dict) -> str:
        source_type = str(item.get("source_type", "") or "").strip()
        path = str(item.get("path", "") or "").strip()

        if source_type == "library_file":
            item_id = str(item.get("item_id", "") or "").strip()
            if item_id:
                return f"/file/{item_id}"

        if source_type == "system_file" and path:
            section = str(item.get("section", "") or "").strip()
            area_key = "knowledge_runtime"
            if section == "visual_web":
                area_key = "web_tools"
            elif section == "memory_related":
                area_key = "memory_qdrant"
            elif section == "library":
                area_key = "library_sources"
            return f"/system-file?area_key={area_key}&file_path={path}"

        return ""

    def _stage_for_mark(self, item: dict) -> str:
        if bool(item.get("promoted", False)):
            return "promoted"
        if bool(item.get("index_ready", False)):
            return "indexed"
        if bool(item.get("summary_ready", False)):
            return "summarized"
        return "marked"

    def _buttons_for_stage(self, item: dict, stage: str) -> dict:
        has_item_id = bool(str(item.get("item_id", "") or "").strip())
        source_type = str(item.get("source_type", "") or "").strip()

        return {
            "can_open": bool(item.get("open_url", "")),
            "can_unmark": True,
            "can_link": source_type == "system_file" and not has_item_id,
            "can_summarize": has_item_id and stage == "marked",
            "can_index": has_item_id and stage == "summarized",
            "can_promote": has_item_id and stage == "indexed",
        }

    def _normalize_path_for_match(self, path: str) -> str:
        clean_path = str(path or "").strip()
        if not clean_path:
            return ""
        clean_path = clean_path.replace("/", "\\")
        try:
            # Windows-friendly: absolute + normalized separators + normalized case.
            # Avoid strict resolve so missing files don't crash matching.
            normalized = os.path.normcase(os.path.normpath(os.path.abspath(clean_path)))
        except Exception:
            normalized = os.path.normcase(os.path.normpath(clean_path))
        return str(normalized).strip()

    def _find_library_item_by_path(self, path: str) -> dict | None:
        normalized_target = self._normalize_path_for_match(path)
        if not normalized_target:
            return None

        library_map = self.facade.get_library_map()
        items = library_map.get("items", []) if isinstance(library_map, dict) else []
        for item in items:
            if not isinstance(item, dict):
                continue
            normalized_item_path = self._normalize_path_for_match(str(item.get("absolute_path", "")))
            if normalized_item_path and normalized_item_path == normalized_target:
                return item
        return None

    def get_workspace_payload(self) -> dict:
        marks = self.marks.list_marks()

        grouped: dict[str, list[dict]] = {
            "marked": [],
            "summarized": [],
            "indexed": [],
            "promoted": [],
        }

        for raw_item in marks:
            item = dict(raw_item)
            item["open_url"] = self._open_url_for_mark(item)

            stage = self._stage_for_mark(item)
            item["stage"] = stage
            item["actions"] = self._buttons_for_stage(item, stage)

            grouped[stage].append(item)

        boxes: list[dict] = []
        total = 0
        for key, label in self.BOX_ORDER:
            items = grouped.get(key, [])
            total += len(items)
            boxes.append(
                {
                    "key": key,
                    "label": label,
                    "count": len(items),
                    "items": items,
                }
            )

        return {
            "boxes": boxes,
            "total_count": total,
        }

    def unmark(self, mark_id: str) -> bool:
        return self.marks.unmark_item(mark_id)

    def refresh_mark(self, mark_id: str) -> dict:
        return self.marks.refresh_mark(mark_id)

    def get_mark(self, mark_id: str) -> dict | None:
        return self.marks.get_mark(mark_id)

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
        return self.marks.update_mark_state(
            mark_id,
            status=status,
            summary_ready=summary_ready,
            index_ready=index_ready,
            promoted=promoted,
            notes=notes,
            last_error=last_error,
        )

    def link_mark_to_library(self, mark_id: str) -> dict:
        mark = self.get_mark(mark_id)
        if mark is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        linked = self._find_library_item_by_path(str(mark.get("path", "")))
        if linked is None:
            raise ValueError("No library item found for this path. Scan the library first.")

        refreshed = self.marks.mark_item(
            source_type="library_file",
            section=str(mark.get("section", "library")),
            file_name=str(linked.get("file_name", "") or mark.get("file_name", "")),
            path=str(linked.get("absolute_path", "") or mark.get("path", "")),
            extension=str(linked.get("extension", "") or mark.get("extension", "")),
            item_id=str(linked.get("item_id", "")).strip() or None,
            root_name=str(linked.get("root_name", "") or mark.get("root_name", "")),
            sha1=str(linked.get("sha1", "") or mark.get("sha1", "")),
            size_bytes=int(linked.get("size_bytes", 0) or mark.get("size_bytes", 0) or 0),
            notes=str(mark.get("notes", "")),
            tags=list(mark.get("tags", []) or []),
        )
        self.update_mark_state(
            refreshed["mark_id"],
            status="linked",
            last_error="",
        )
        return refreshed

    def summarize_mark(self, mark_id: str) -> dict:
        mark = self.get_mark(mark_id)
        if mark is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        item_id = str(mark.get("item_id", "") or "").strip()
        if not item_id:
            raise ValueError("This marked item is not linked to a library item_id yet.")

        result = self.facade.summarize_file(item_id=item_id)
        self.update_mark_state(
            mark_id,
            status="summarized",
            summary_ready=True,
            last_error="",
        )
        return result

    def index_mark(self, mark_id: str) -> dict:
        mark = self.get_mark(mark_id)
        if mark is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        item_id = str(mark.get("item_id", "") or "").strip()
        if not item_id:
            raise ValueError("This marked item is not linked to a library item_id yet.")

        result = self.facade.index_file(item_id=item_id)
        self.update_mark_state(
            mark_id,
            status="indexed",
            index_ready=True,
            last_error="",
        )
        return result

    def promote_mark(self, mark_id: str) -> dict:
        mark = self.get_mark(mark_id)
        if mark is None:
            raise ValueError(f"Unknown mark_id: {mark_id}")

        item_id = str(mark.get("item_id", "") or "").strip()
        if not item_id:
            raise ValueError("This marked item is not linked to a library item_id yet.")

        result = self.facade.promote_to_context_memory(item_id=item_id)
        self.update_mark_state(
            mark_id,
            status="promoted",
            promoted=True,
            last_error="",
        )
        return result
