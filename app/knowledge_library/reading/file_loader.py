from __future__ import annotations

from pathlib import Path

from .docx_reader import DocxReaderService
from .pdf_reader import PdfReaderService
from .text_reader import TextReader


class FileLoader:
    def __init__(self) -> None:
        self.text_reader = TextReader()
        self.pdf_reader = PdfReaderService()
        self.docx_reader = DocxReaderService()

    def load_text(self, path: str | Path) -> tuple[str, dict]:
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower().strip()

        if ext in {".txt", ".md", ".json", ".csv", ".log"}:
            text = self.text_reader.read(file_path)
        elif ext == ".pdf":
            text = self.pdf_reader.read(file_path)
        elif ext == ".docx":
            text = self.docx_reader.read(file_path)
        else:
            raise ValueError(f"Unsupported extension: {ext}")

        return text, {
            "absolute_path": str(file_path.resolve()),
            "file_name": file_path.name,
            "extension": ext,
        }