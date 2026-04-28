from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.backends.mem0.mem0_adapter import Mem0Adapter
from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class Mem0MemoryStore:
    mem0_adapter: Mem0Adapter

    def save_memory_items(self, items: list[MemoryItem]) -> None:
        for item in items:
            self.mem0_adapter.add(
                text=item.text,
                metadata={
                    "item_id": item.item_id,
                    "kind": item.kind,
                    "source": item.source,
                    "importance": item.importance,
                    "ts": item.ts,
                    "tags": item.tags,
                    "related_ids": item.related_ids,
                    "project_name": item.project_name,
                    "metadata": item.metadata,
                },
            )

    def load_memory_items(self) -> list[MemoryItem]:
        raw_items = self.mem0_adapter.dump_all()
        result: list[MemoryItem] = []

        for index, raw in enumerate(raw_items):
            text = str(raw.get("text") or "").strip()
            metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
            if not text:
                continue

            result.append(
                MemoryItem(
                    item_id=str(metadata.get("item_id") or f"mem0_item_{index}"),
                    text=text,
                    kind=str(metadata.get("kind") or "general_memory"),
                    source=str(metadata.get("source") or "mem0"),
                    importance=float(metadata.get("importance") or 0.5),
                    ts=float(metadata["ts"]) if metadata.get("ts") is not None else None,
                    tags=list(metadata.get("tags") or []),
                    related_ids=list(metadata.get("related_ids") or []),
                    project_name=(
                        str(metadata.get("project_name"))
                        if metadata.get("project_name") is not None
                        else None
                    ),
                    metadata=dict(metadata.get("metadata") or {}),
                )
            )

        return result