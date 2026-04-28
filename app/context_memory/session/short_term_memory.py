from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass(slots=True)
class ShortTermMemory:
    limit: int = 40
    items: deque[str] = field(default_factory=deque)

    def add(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return

        self.items.append(cleaned)

        while len(self.items) > self.limit:
            self.items.popleft()

    def extend(self, items: list[str]) -> None:
        for item in items:
            self.add(item)

    def get_all(self) -> list[str]:
        return list(self.items)

    def get_recent(self, limit: int = 20) -> list[str]:
        if limit <= 0:
            return []
        return list(self.items)[-limit:]

    def clear(self) -> None:
        self.items.clear()

    def size(self) -> int:
        return len(self.items)