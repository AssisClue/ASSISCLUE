from __future__ import annotations

import json
from pathlib import Path


class WorkspaceMarksStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[dict]:
        if not self.path.exists() or not self.path.is_file():
            return []

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return []

        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
        return []

    def save(self, payload: list[dict]) -> None:
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )