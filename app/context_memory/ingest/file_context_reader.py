from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.context_memory.contracts.input_types import FileContextInput


@dataclass(slots=True)
class FileContextReader:
    file_paths: list[str | Path] = field(default_factory=list)
    encoding: str = "utf-8"

    def read(self) -> list[FileContextInput]:
        items: list[FileContextInput] = []

        for raw_path in self.file_paths:
            path = Path(raw_path)
            if not path.exists() or not path.is_file():
                continue

            try:
                text = path.read_text(encoding=self.encoding)
            except UnicodeDecodeError:
                continue
            except OSError:
                continue

            cleaned = text.strip()
            if not cleaned:
                continue

            items.append(
                FileContextInput(
                    path=str(path),
                    text=cleaned,
                    ts=self._get_mtime(path),
                    source="file_context",
                    metadata={
                        "filename": path.name,
                        "suffix": path.suffix,
                    },
                )
            )

        return items

    @staticmethod
    def _get_mtime(path: Path) -> float | None:
        try:
            return path.stat().st_mtime
        except OSError:
            return None