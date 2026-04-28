from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class MemoryRecordBuilder:
    def build(
        self,
        item_id: str,
        text: str,
        kind: str,
        source: str,
        importance: float,
        ts: float | None = None,
        tags: list[str] | None = None,
        project_name: str | None = None,
        metadata: dict | None = None,
    ) -> MemoryItem:
        return MemoryItem(
            item_id=item_id,
            text=text.strip(),
            kind=kind,
            source=source.strip(),
            importance=importance,
            ts=ts,
            tags=list(tags or []),
            project_name=project_name,
            metadata=dict(metadata or {}),
        )