from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class DailyContextSummary:
    def build_lines(self, items: list[MemoryItem], max_items: int = 12) -> list[str]:
        sorted_items = sorted(items, key=lambda item: (item.ts or 0.0, item.importance), reverse=True)

        lines: list[str] = []
        for item in sorted_items:
            if not item.text.strip():
                continue

            prefix = item.kind.replace("_", " ").strip()
            lines.append(f"[{prefix}] {item.text}")

            if len(lines) >= max_items:
                break

        return lines