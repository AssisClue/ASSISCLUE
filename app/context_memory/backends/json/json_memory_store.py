from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class JsonMemoryStore:
    storage_path: str | Path

    def __post_init__(self) -> None:
        self.storage_path = Path(self.storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]", encoding="utf-8")

    def save_memory_items(self, items: list[MemoryItem]) -> None:
        payload = [asdict(item) for item in items]
        self.storage_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_memory_items(self) -> list[MemoryItem]:
        raw = self.storage_path.read_text(encoding="utf-8").strip()
        if not raw:
            return []

        data = json.loads(raw)
        if not isinstance(data, list):
            return []

        items: list[MemoryItem] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            items.append(MemoryItem(**item))
        return items