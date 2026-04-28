from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RelationExtractor:
    def extract_keywords(self, text: str) -> set[str]:
        cleaned = text.strip().lower()
        if not cleaned:
            return set()

        words = {
            token.strip(".,!?;:\"'()[]{}")
            for token in cleaned.split()
            if token.strip(".,!?;:\"'()[]{}")
        }
        return {word for word in words if len(word) >= 4}

    def is_related(self, left_text: str, right_text: str, min_overlap: int = 2) -> bool:
        left_words = self.extract_keywords(left_text)
        right_words = self.extract_keywords(right_text)

        if not left_words or not right_words:
            return False

        overlap = left_words.intersection(right_words)
        return len(overlap) >= min_overlap