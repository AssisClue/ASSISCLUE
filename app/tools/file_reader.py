from __future__ import annotations

from pathlib import Path


def read_text_file(path: str | Path) -> str:
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8")


def safe_read_text_file(path: str | Path) -> str:
    file_path = Path(path)

    if not file_path.exists():
        return ""

    if not file_path.is_file():
        return ""

    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        return ""