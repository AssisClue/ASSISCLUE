from __future__ import annotations

from .library_admin_service import LibraryAdminService
from .library_service import LibraryService
from .reading_service import ReadingService
from .indexing_service import IndexingService
from .promotion_service import PromotionService


class KnowledgeLibraryFacade:
    def __init__(self) -> None:
        self.admin = LibraryAdminService()
        self.library = LibraryService()
        self.reading = ReadingService()
        self.indexing = IndexingService()
        self.promotion = PromotionService()

    # roots
    def register_root(self, *, name: str, path: str, kind: str = "library", tags: list[str] | None = None) -> dict:
        root = self.admin.register_root(name=name, path=path, kind=kind, tags=tags)
        return {
            "root_id": root.root_id,
            "name": root.name,
            "path": root.path,
            "kind": root.kind,
            "tags": list(root.tags),
            "enabled": bool(root.enabled),
        }

    def list_roots(self) -> list[dict]:
        roots = self.admin.list_roots()
        return [
            {
                "root_id": root.root_id,
                "name": root.name,
                "path": root.path,
                "kind": root.kind,
                "tags": list(root.tags),
                "enabled": bool(root.enabled),
            }
            for root in roots
        ]

    def remove_root(self, root_id: str) -> bool:
        return self.admin.remove_root(root_id)

    # scan
    def scan_all(self) -> dict:
        return self.library.scan_all()

    def get_library_map(self) -> dict:
        return self.library.get_library_map()

    # read
    def read_file(self, *, item_id: str | None = None, absolute_path: str | None = None, max_chars: int | None = None) -> dict:
        return self.reading.read_file(item_id=item_id, absolute_path=absolute_path, max_chars=max_chars)

    def read_chapter(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        chapter_number: int | None = None,
        chapter_title_hint: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        return self.reading.read_chapter(
            item_id=item_id,
            absolute_path=absolute_path,
            chapter_number=chapter_number,
            chapter_title_hint=chapter_title_hint,
            max_chars=max_chars,
        )

    def find_paragraphs(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        query: str,
        limit: int = 3,
        max_chars_per_result: int = 500,
    ) -> dict:
        return self.reading.find_paragraphs(
            item_id=item_id,
            absolute_path=absolute_path,
            query=query,
            limit=limit,
            max_chars_per_result=max_chars_per_result,
        )

    # summarize / index
    def summarize_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int = 12000,
        max_summary_chars: int = 800,
    ) -> dict:
        return self.indexing.summarize_file(
            item_id=item_id,
            absolute_path=absolute_path,
            max_chars=max_chars,
            max_summary_chars=max_summary_chars,
        )

    def index_file(
        self,
        *,
        item_id: str,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        write_vectors: bool = False,
        make_summary: bool = True,
    ) -> dict:
        return self.indexing.index_file(
            item_id=item_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            make_summary=make_summary,
        )

    # promote
    def promote_to_context_memory(
        self,
        *,
        item_id: str,
        rebuild_qdrant: bool = False,
    ) -> dict:
        return self.promotion.promote_to_context_memory(
            item_id=item_id,
            rebuild_qdrant=rebuild_qdrant,
        )