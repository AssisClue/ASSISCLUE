from __future__ import annotations

from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.contracts.reading_types import ReadResult
from app.knowledge_library.reading.chapter_locator import ChapterLocator
from app.knowledge_library.reading.file_loader import FileLoader
from app.knowledge_library.reading.paragraph_locator import ParagraphLocator
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class ReadFilePipeline:
    def __init__(self) -> None:
        self.loader = FileLoader()
        self.chapter_locator = ChapterLocator()
        self.paragraph_locator = ParagraphLocator()
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.map_store = LibraryMapStore(self.paths.library_map_path())

    def _resolve_path_from_item_id(self, item_id: str) -> str:
        raw = self.map_store.load(default={})
        items = raw.get("items", []) if isinstance(raw, dict) else []
        for item in items:
            if str(item.get("item_id", "")).strip() == str(item_id).strip():
                return str(item.get("absolute_path", "")).strip()
        raise ValueError(f"Unknown item_id: {item_id}")

    def read(self, *, item_id: str | None = None, absolute_path: str | None = None, max_chars: int | None = None) -> ReadResult:
        path = absolute_path or self._resolve_path_from_item_id(str(item_id or "").strip())
        text, meta = self.loader.load_text(path)

        if max_chars is not None and max_chars > 0:
            text = text[:max_chars]

        return ReadResult(
            ok=True,
            source_path=meta["absolute_path"],
            file_name=meta["file_name"],
            extension=meta["extension"],
            text=text,
            text_length=len(text),
            metadata={},
        )

    def read_chapter(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        chapter_number: int | None = None,
        chapter_title_hint: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        result = self.read(item_id=item_id, absolute_path=absolute_path, max_chars=None)
        chapter = self.chapter_locator.locate(
            text=result.text,
            chapter_number=chapter_number,
            chapter_title_hint=chapter_title_hint,
            max_chars=max_chars,
        )
        if chapter is None:
            return {
                "ok": False,
                "reason": "chapter_not_found",
                "source_path": result.source_path,
                "file_name": result.file_name,
            }

        return {
            "ok": True,
            "source_path": result.source_path,
            "file_name": result.file_name,
            "chapter": chapter.to_dict(),
        }

    def find_paragraphs(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        query: str,
        limit: int = 3,
        max_chars_per_result: int = 500,
    ) -> dict:
        result = self.read(item_id=item_id, absolute_path=absolute_path, max_chars=None)
        matches = self.paragraph_locator.find(
            text=result.text,
            query=query,
            limit=limit,
            max_chars_per_result=max_chars_per_result,
        )
        return {
            "ok": True,
            "source_path": result.source_path,
            "file_name": result.file_name,
            "query": query,
            "match_count": len(matches),
            "matches": matches,
        }