from __future__ import annotations

from pathlib import Path


DEFAULT_ALLOWED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".json",
    ".jsonl",
    ".csv",
    ".log",
    ".html",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
}


class FolderScanner:
    def __init__(self, allowed_extensions: set[str] | None = None) -> None:
        self.allowed_extensions = {
            ext.lower().strip() for ext in (allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS)
        }

    def iter_files(self, root_path: Path) -> list[Path]:
        if not root_path.exists() or not root_path.is_dir():
            return []

        files: list[Path] = []
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.allowed_extensions:
                continue
            files.append(path)
        return sorted(files, key=lambda p: str(p).lower())
