from __future__ import annotations

from .service_parts.actions_service import ActionsService
from .service_parts.area_service import AreaViewService
from .service_parts.home_service import HomeViewService
from .service_parts.library_file_service import LibraryFileViewService
from app.knowledge_library.workspace_marks.marks_service import WorkspaceMarksService


class LibraryUiService:
    def __init__(self) -> None:
        self.home = HomeViewService()
        self.library_files = LibraryFileViewService()
        self.areas = AreaViewService()
        self.actions = ActionsService()
        self.marks = WorkspaceMarksService()

    def get_home_payload(
        self,
        *,
        search: str = "",
        extension: str = "",
        root_id: str = "",
    ) -> dict:
        return self.home.get_home_payload(
            search=search,
            extension=extension,
            root_id=root_id,
        )

    def get_item_by_id(self, item_id: str) -> dict:
        return self.library_files.get_item_by_id(item_id)

    def get_file_payload(self, item_id: str) -> dict:
        return self.library_files.get_file_payload(item_id)

    def get_area_payload(self, area_key: str) -> dict:
        return self.areas.get_area_payload(area_key)

    def get_area_browser_payload(
        self,
        area_key: str,
        *,
        current_path: str = "",
        search: str = "",
        extension: str = "",
        entry_type: str = "",
    ) -> dict:
        return self.areas.get_area_browser_payload(
            area_key,
            current_path=current_path,
            search=search,
            extension=extension,
            entry_type=entry_type,
        )

    def get_system_file_payload(self, area_key: str, file_path: str) -> dict:
        return self.areas.get_system_file_payload(area_key, file_path)

    def scan_all(self) -> dict:
        return self.actions.scan_all()

    def summarize_file(self, item_id: str) -> dict:
        return self.actions.summarize_file(item_id)

    def index_file(self, item_id: str) -> dict:
        return self.actions.index_file(item_id)

    def promote_file(self, item_id: str) -> dict:
        return self.actions.promote_file(item_id)

    def mark_library_file(self, item_id: str) -> dict:
        item = self.get_item_by_id(item_id)
        return self.marks.mark_item(
            source_type="library_file",
            section="library",
            file_name=str(item.get("file_name", "")),
            path=str(item.get("absolute_path", "")),
            extension=str(item.get("extension", "")),
            item_id=str(item.get("item_id", "")).strip() or None,
            root_name=str(item.get("root_name", "")),
            sha1=str(item.get("sha1", "")),
            size_bytes=int(item.get("size_bytes", 0) or 0),
            tags=list(item.get("tags", []) or []),
        )

    def _guess_system_section(self, area_key: str) -> str:
        clean = str(area_key or "").strip().lower()
        if clean in {"library_sources"}:
            return "library"
        if clean in {"knowledge_runtime"}:
            return "knowledge_runtime"
        if clean in {"display_actions", "web_tools"}:
            return "visual_web"
        if clean in {"memory_qdrant"}:
            return "memory_related"
        return "knowledge_runtime"

    def mark_system_file(self, area_key: str, file_path: str) -> dict:
        payload = self.get_system_file_payload(area_key, file_path)
        entry = payload["entry"]
        return self.marks.mark_item(
            source_type="system_file",
            section=self._guess_system_section(area_key),
            file_name=str(entry.get("name", "")),
            path=str(entry.get("path", "")),
            extension=str(entry.get("extension", "")),
            size_bytes=int(entry.get("size_bytes", 0) or 0),
            notes=f"Marked from system area: {area_key}",
        )

    def list_workspace_marks(self) -> list[dict]:
        return self.marks.list_marks()

    def unmark_item(self, mark_id: str) -> bool:
        return self.marks.unmark_item(mark_id)

    def refresh_mark(self, mark_id: str) -> dict:
        return self.marks.refresh_mark(mark_id)

    def get_mark(self, mark_id: str) -> dict | None:
        return self.marks.get_mark(mark_id)

    def find_mark_by_path(self, path: str) -> dict | None:
        return self.marks.find_mark_by_path(path)

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