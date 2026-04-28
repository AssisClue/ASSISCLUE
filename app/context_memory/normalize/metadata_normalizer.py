from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MetadataNormalizer:
    def normalize(self, metadata: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(metadata, dict):
            return {}

        normalized: dict[str, Any] = {}
        for key, value in metadata.items():
            normalized_key = str(key).strip()
            if not normalized_key:
                continue
            normalized[normalized_key] = value

        return normalized