from __future__ import annotations

from app.knowledge_library.indexing.chunker import TextChunker
from app.knowledge_library.indexing.summary_builder import SummaryBuilder
from app.knowledge_library.indexing.vector_index_writer import VectorIndexWriter
from app.knowledge_library.models.indexing_job import IndexingJob
from app.knowledge_library.models.summary_record import SummaryRecord
from app.knowledge_library.reading.file_loader import FileLoader


class IndexPipeline:
    def __init__(self) -> None:
        self.loader = FileLoader()
        self.chunker = TextChunker()
        self.summary_builder = SummaryBuilder()
        self.vector_writer = VectorIndexWriter()

    def run(
        self,
        *,
        item_id: str,
        absolute_path: str,
        file_name: str,
        chunk_size: int,
        chunk_overlap: int,
        write_vectors: bool,
        make_summary: bool,
        max_summary_chars: int = 800,
    ) -> tuple[IndexingJob, list[dict], SummaryRecord | None, dict]:
        text, _meta = self.loader.load_text(absolute_path)
        chunks = self.chunker.chunk_text(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        summary = None
        if make_summary:
            summary = SummaryRecord(
                item_id=item_id,
                source_path=absolute_path,
                file_name=file_name,
                summary_text=self.summary_builder.build_summary(
                    text=text,
                    max_summary_chars=max_summary_chars,
                ),
            )

        vector_result = self.vector_writer.write_chunks(
            chunks=chunks,
            write_vectors=write_vectors,
        )

        job = IndexingJob(
            job_id=f"index::{item_id}",
            item_id=item_id,
            source_path=absolute_path,
            file_name=file_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            status="completed",
            chunk_count=len(chunks),
        )

        return job, chunks, summary, vector_result