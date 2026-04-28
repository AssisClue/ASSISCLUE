from __future__ import annotations

from app.knowledge_library.orchestration.index_file_pipeline import IndexFilePipeline
from app.knowledge_library.orchestration.summarize_file_pipeline import SummarizeFilePipeline


class IndexingService:
    def __init__(self) -> None:
        self.index_pipeline = IndexFilePipeline()
        self.summary_pipeline = SummarizeFilePipeline()

    def summarize_file(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int = 12000,
        max_summary_chars: int = 800,
    ) -> dict:
        return self.summary_pipeline.summarize(
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
        return self.index_pipeline.index_file(
            item_id=item_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            make_summary=make_summary,
        )