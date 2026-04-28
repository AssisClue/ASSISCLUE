from __future__ import annotations

from app.mcp.services.knowledge_library_mcp_service import KnowledgeLibraryMcpService

_service = KnowledgeLibraryMcpService()


def list_library_roots() -> dict:
    return _service.list_library_roots()


def register_library_root(
    *,
    name: str,
    path: str,
    kind: str = "library",
    tags: list[str] | None = None,
) -> dict:
    return _service.register_library_root(
        name=name,
        path=path,
        kind=kind,
        tags=tags,
    )


def scan_library() -> dict:
    return _service.scan_library()


def read_library_map() -> dict:
    return _service.read_library_map()


def read_library_file(
    *,
    item_id: str | None = None,
    absolute_path: str | None = None,
    max_chars: int | None = None,
) -> dict:
    return _service.read_library_file(
        item_id=item_id,
        absolute_path=absolute_path,
        max_chars=max_chars,
    )


def read_library_chapter(
    *,
    item_id: str | None = None,
    absolute_path: str | None = None,
    chapter_number: int | None = None,
    chapter_title_hint: str | None = None,
    max_chars: int | None = None,
) -> dict:
    return _service.read_library_chapter(
        item_id=item_id,
        absolute_path=absolute_path,
        chapter_number=chapter_number,
        chapter_title_hint=chapter_title_hint,
        max_chars=max_chars,
    )


def find_library_paragraphs(
    *,
    item_id: str | None = None,
    absolute_path: str | None = None,
    query: str,
    limit: int = 3,
    max_chars_per_result: int = 500,
) -> dict:
    return _service.find_library_paragraphs(
        item_id=item_id,
        absolute_path=absolute_path,
        query=query,
        limit=limit,
        max_chars_per_result=max_chars_per_result,
    )


def summarize_library_file(
    *,
    item_id: str | None = None,
    absolute_path: str | None = None,
    max_chars: int = 12000,
    max_summary_chars: int = 800,
) -> dict:
    return _service.summarize_library_file(
        item_id=item_id,
        absolute_path=absolute_path,
        max_chars=max_chars,
        max_summary_chars=max_summary_chars,
    )


def index_library_file(
    *,
    item_id: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    write_vectors: bool = False,
    make_summary: bool = True,
) -> dict:
    return _service.index_library_file(
        item_id=item_id,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        write_vectors=write_vectors,
        make_summary=make_summary,
    )


def promote_library_file_to_memory(
    *,
    item_id: str,
    rebuild_qdrant: bool = False,
) -> dict:
    return _service.promote_library_file_to_memory(
        item_id=item_id,
        rebuild_qdrant=rebuild_qdrant,
    )