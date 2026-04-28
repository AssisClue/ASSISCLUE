from __future__ import annotations

from app.knowledge_library.services.knowledge_library_facade import KnowledgeLibraryFacade


class KnowledgeLibraryAdapter:
    def __init__(self) -> None:
        self.facade = KnowledgeLibraryFacade()

    def list_roots(self) -> list[dict]:
        return self.facade.list_roots()

    def register_root(
        self,
        *,
        name: str,
        path: str,
        kind: str = "library",
        tags: list[str] | None = None,
    ) -> dict:
        return self.facade.register_root(
            name=name,
            path=path,
            kind=kind,
            tags=tags,
        )

    def scan_all(self) -> dict:
        return self.facade.scan_all()

    def get_library_map(self) -> dict:
        return self.facade.get_library_map()

    def read_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        return self.facade.read_file(
            item_id=item_id,
            absolute_path=absolute_path,
            max_chars=max_chars,
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
        return self.facade.read_chapter(
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
        return self.facade.find_paragraphs(
            item_id=item_id,
            absolute_path=absolute_path,
            query=query,
            limit=limit,
            max_chars_per_result=max_chars_per_result,
        )

    def summarize_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int = 12000,
        max_summary_chars: int = 800,
    ) -> dict:
        return self.facade.summarize_file(
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
        return self.facade.index_file(
            item_id=item_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            make_summary=make_summary,
        )

    def promote_to_context_memory(
        self,
        *,
        item_id: str,
        rebuild_qdrant: bool = False,
    ) -> dict:
        return self.facade.promote_to_context_memory(
            item_id=item_id,
            rebuild_qdrant=rebuild_qdrant,
        )