from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.summarize.daily_context_summary import DailyContextSummary


@dataclass(slots=True)
class DailySnapshotService:
    daily_context_summary: DailyContextSummary

    def build_daily_lines(self, items: list[MemoryItem], max_items: int = 12) -> list[str]:
        return self.daily_context_summary.build_lines(items=items, max_items=max_items)