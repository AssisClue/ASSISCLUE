from __future__ import annotations

from app.mcp.adapters.knowledge_library_adapter import KnowledgeLibraryAdapter


class KnowledgeLibraryMcpService:
    def __init__(self) -> None:
        self.adapter = KnowledgeLibraryAdapter()

    def list_library_roots(self) -> dict:
        return {
            "ok": True,
            "roots": self.adapter.list_roots(),
            "count": len(self.adapter.list_roots()),
        }

    def register_library_root(
        self,
        *,
        name: str,
        path: str,
        kind: str = "library",
        tags: list[str] | None = None,
    ) -> dict:
        root = self.adapter.register_root(
            name=name,
            path=path,
            kind=kind,
            tags=tags,
        )
        return {
            "ok": True,
            "root": root,
        }

    def scan_library(self) -> dict:
        result = self.adapter.scan_all()
        return {
            "ok": True,
            **result,
        }

    def read_library_map(self) -> dict:
        payload = self.adapter.get_library_map()
        return {
            "ok": True,
            "library_map": payload,
        }

    def read_library_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        return self.adapter.read_file(
            item_id=item_id,
            absolute_path=absolute_path,
            max_chars=max_chars,
        )

    def read_library_chapter(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        chapter_number: int | None = None,
        chapter_title_hint: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        return self.adapter.read_chapter(
            item_id=item_id,
            absolute_path=absolute_path,
            chapter_number=chapter_number,
            chapter_title_hint=chapter_title_hint,
            max_chars=max_chars,
        )

    def find_library_paragraphs(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        query: str,
        limit: int = 3,
        max_chars_per_result: int = 500,
    ) -> dict:
        return self.adapter.find_paragraphs(
            item_id=item_id,
            absolute_path=absolute_path,
            query=query,
            limit=limit,
            max_chars_per_result=max_chars_per_result,
        )

    def summarize_library_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int = 12000,
        max_summary_chars: int = 800,
    ) -> dict:
        return self.adapter.summarize_file(
            item_id=item_id,
            absolute_path=absolute_path,
            max_chars=max_chars,
            max_summary_chars=max_summary_chars,
        )

    def index_library_file(
        self,
        *,
        item_id: str,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        write_vectors: bool = False,
        make_summary: bool = True,
    ) -> dict:
        return self.adapter.index_file(
            item_id=item_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            make_summary=make_summary,
        )

    def promote_library_file_to_memory(
        self,
        *,
        item_id: str,
        rebuild_qdrant: bool = False,
    ) -> dict:
        return self.adapter.promote_to_context_memory(
            item_id=item_id,
            rebuild_qdrant=rebuild_qdrant,
        )