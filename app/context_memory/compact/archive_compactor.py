from __future__ import annotations

import time
from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class ArchiveCompactor:
    archive_after_seconds: float = 60 * 60 * 24 * 30

    def split_active_and_archive(self, items: list[MemoryItem]) -> tuple[list[MemoryItem], list[MemoryItem]]:
        now = time.time()
        active: list[MemoryItem] = []
        archived: list[MemoryItem] = []

        for item in items:
            if item.ts is None:
                active.append(item)
                continue

            age = max(now - item.ts, 0.0)
            if age >= self.archive_after_seconds:
                archived.append(item)
            else:
                active.append(item)

        return active, archived
    