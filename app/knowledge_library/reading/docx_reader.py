from __future__ import annotations

from pathlib import Path

from docx import Document


class DocxReaderService:
    def read(self, path: Path) -> str:
        doc = Document(str(path))
        parts = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(parts).strip()