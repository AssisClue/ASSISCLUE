from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class UserProfileMemory:
    profile_items: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        cleaned = text.strip()
        if cleaned and cleaned not in self.profile_items:
            self.profile_items.append(cleaned)

    def extend(self, items: list[str]) -> None:
        for item in items:
            self.add(item)

    def get_all(self) -> list[str]:
        return list(self.profile_items)

    def clear(self) -> None:
        self.profile_items.clear()

    def size(self) -> int:
        return len(self.profile_items)