from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LibraryMapStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self, default: Any) -> Any:
        if not self.path.exists() or not self.path.is_file():
            return default
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return default

    def save(self, payload: Any) -> None:
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )