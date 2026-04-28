from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from .qdrant_runtime_config import CONTEXT_MEMORY_QDRANT_VECTOR_SIZE


def _tokenize(text: str) -> list[str]:
    cleaned = str(text or "").lower()
    for ch in ",.?;:!\"'()[]{}<>/\\|@#$%^&*+-=_~`":
        cleaned = cleaned.replace(ch, " ")
    return [token for token in cleaned.split() if token]


@dataclass(slots=True)
class QdrantTextEmbedder:
    vector_size: int = CONTEXT_MEMORY_QDRANT_VECTOR_SIZE

    def embed_text(self, text: str) -> list[float]:
        size = max(8, int(self.vector_size or 256))
        vector = [0.0] * size

        tokens = _tokenize(text)
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % size
            sign = 1.0 if (digest[4] % 2 == 0) else -1.0
            weight = 1.0 + (min(len(token), 12) / 12.0)
            vector[idx] += sign * weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm <= 0.0:
            return vector

        return [value / norm for value in vector]