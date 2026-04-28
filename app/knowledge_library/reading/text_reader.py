from __future__ import annotations

from pathlib import Path


class TextReader:
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")