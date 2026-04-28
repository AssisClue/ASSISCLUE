from __future__ import annotations

from app.knowledge_library.backends.json.library_map_store import LibraryMapStore
from app.knowledge_library.backends.json.summary_store import SummaryStore
from app.knowledge_library.indexing.summary_builder import SummaryBuilder
from app.knowledge_library.reading.file_loader import FileLoader
from app.knowledge_library.runtime.storage_paths import KnowledgeLibraryStoragePaths


class SummarizeFilePipeline:
    def __init__(self) -> None:
        self.loader = FileLoader()
        self.builder = SummaryBuilder()
        self.paths = KnowledgeLibraryStoragePaths()
        self.paths.ensure_directories()
        self.map_store = LibraryMapStore(self.paths.library_map_path())
        self.summary_store = SummaryStore(self.paths.runtime_root() / "summaries" / "file_summaries.jsonl")

    def _resolve_item(self, item_id: str) -> dict:
        raw = self.map_store.load(default={})
        items = raw.get("items", []) if isinstance(raw, dict) else []
        for item in items:
            if str(item.get("item_id", "")).strip() == str(item_id).strip():
                return item
        raise ValueError(f"Unknown item_id: {item_id}")

    def summarize(
        self,
        *,
        item_id: str | None = None,
        absolute_path: str | None = None,
        max_chars: int = 12000,
        max_summary_chars: int = 800,
    ) -> dict:
        resolved_item = None
        path = absolute_path

        if item_id:
            resolved_item = self._resolve_item(item_id)
            path = str(resolved_item.get("absolute_path", "")).strip()

        text, meta = self.loader.load_text(path)
        if max_chars > 0:
            text = text[:max_chars]

        summary = self.builder.build_summary(text=text, max_summary_chars=max_summary_chars)

        payload = {
            "item_id": str((resolved_item or {}).get("item_id", "")).strip(),
            "source_path": meta["absolute_path"],
            "file_name": meta["file_name"],
            "summary_text": summary,
            "summary_kind": "extractive",
        }
        self.summary_store.append(payload)
        return {"ok": True, **payload}