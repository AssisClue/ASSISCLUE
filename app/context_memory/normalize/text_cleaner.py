from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TextCleaner:
    def clean(self, text: str) -> str:
        return " ".join(text.strip().split())