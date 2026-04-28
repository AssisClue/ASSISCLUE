from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.normalize.memory_text_normalizer import normalize_memory_text


@dataclass(slots=True)
class RecentContextCompactor:
    def compact(self, lines: list[str], max_items: int = 20) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for line in lines:
            cleaned = line.strip()
            if not cleaned:
                continue

            key = normalize_memory_text(cleaned)
            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result[:max_items]