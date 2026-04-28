from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PreferenceStore:
    preferences: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        cleaned = text.strip()
        if cleaned and cleaned not in self.preferences:
            self.preferences.append(cleaned)

    def extend(self, items: list[str]) -> None:
        for item in items:
            self.add(item)

    def get_all(self) -> list[str]:
        return list(self.preferences)

    def clear(self) -> None:
        self.preferences.clear()

    def size(self) -> int:
        return len(self.preferences)