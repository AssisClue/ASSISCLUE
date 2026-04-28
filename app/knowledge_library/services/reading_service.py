from __future__ import annotations

from app.knowledge_library.orchestration.read_file_pipeline import ReadFilePipeline


class ReadingService:
    def __init__(self) -> None:
        self.pipeline = ReadFilePipeline()

    def read_file(self, *, item_id: str | None = None, absolute_path: str | None = None, max_chars: int | None = None) -> dict:
        result = self.pipeline.read(item_id=item_id, absolute_path=absolute_path, max_chars=max_chars)
        return {
            "ok": result.ok,
            "source_path": result.source_path,
            "file_name": result.file_name,
            "extension": result.extension,
            "text": result.text,
            "text_length": result.text_length,
            "metadata": result.metadata,
        }

    def read_chapter(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        chapter_number: int | None = None,
        chapter_title_hint: str | None = None,
        max_chars: int | None = None,
    ) -> dict:
        return self.pipeline.read_chapter(
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
        return self.pipeline.find_paragraphs(
            item_id=item_id,
            absolute_path=absolute_path,
            query=query,
            limit=limit,
            max_chars_per_result=max_chars_per_result,
        )