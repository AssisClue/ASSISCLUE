from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


class PdfReaderService:
    def read(self, path: Path) -> str:
        reader = PdfReader(str(path))
        parts: list[str] = []

        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                parts.append(f"[PAGE {i}]\n{text}")

        return "\n\n".join(parts).strip()