from __future__ import annotations

import json
from pathlib import Path

from app.knowledge_library.backends.json.index_job_store import IndexJobStore
from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.indexing.index_pipeline import IndexPipeline
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class IndexFilePipeline:
    def __init__(self) -> None:
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.map_store = LibraryMapStore(self.paths.library_map_path())
        self.job_store = IndexJobStore(self.paths.runtime_root() / "indexing" / "jobs.jsonl")
        self.indexed_store = IndexJobStore(self.paths.runtime_root() / "indexing" / "indexed_files.json")
        self.pipeline = IndexPipeline()

    def _resolve_item(self, item_id: str) -> dict:
        raw = self.map_store.load(default={})
        items = raw.get("items", []) if isinstance(raw, dict) else []
        for item in items:
            if str(item.get("item_id", "")).strip() == str(item_id).strip():
                return item
        raise ValueError(f"Unknown item_id: {item_id}")

    def _chunk_manifest_path(self, item_id: str) -> Path:
        return self.paths.runtime_root() / "indexing" / "chunk_manifests" / f"{item_id}.json"

    def index_file(
        self,
        *,
        item_id: str,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
        write_vectors: bool = False,
        make_summary: bool = True,
    ) -> dict:
        item = self._resolve_item(item_id)

        job, chunks, summary, vector_result = self.pipeline.run(
            item_id=str(item["item_id"]),
            absolute_path=str(item["absolute_path"]),
            file_name=str(item["file_name"]),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            write_vectors=write_vectors,
            make_summary=make_summary,
        )

        manifest_path = self._chunk_manifest_path(str(item["item_id"]))
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "item_id": item["item_id"],
                    "source_path": item["absolute_path"],
                    "file_name": item["file_name"],
                    "chunk_count": len(chunks),
                    "chunks": chunks,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        self.job_store.append(job.to_dict())

        indexed_payload = {
            "item_id": str(item["item_id"]),
            "source_path": str(item["absolute_path"]),
            "file_name": str(item["file_name"]),
            "chunk_count": len(chunks),
            "chunk_manifest_path": str(manifest_path),
            "summary_created": bool(summary is not None),
            "vector_result": vector_result,
        }
        self.indexed_store.save_json(indexed_payload)

        if summary is not None:
            summaries_path = self.paths.runtime_root() / "summaries" / "book_summaries.jsonl"
            summaries_path.parent.mkdir(parents=True, exist_ok=True)
            with summaries_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(summary.to_dict(), ensure_ascii=False) + "\n")

        return {
            "ok": True,
            "item_id": str(item["item_id"]),
            "source_path": str(item["absolute_path"]),
            "file_name": str(item["file_name"]),
            "chunk_count": len(chunks),
            "chunk_manifest_path": str(manifest_path),
            "summary_created": bool(summary is not None),
            "vector_result": vector_result,
        }