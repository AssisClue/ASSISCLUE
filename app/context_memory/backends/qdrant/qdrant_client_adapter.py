from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .qdrant_runtime_config import (
    CONTEXT_MEMORY_QDRANT_API_KEY,
    CONTEXT_MEMORY_QDRANT_LOCAL_PATH,
    CONTEXT_MEMORY_QDRANT_MODE,
    CONTEXT_MEMORY_QDRANT_URL,
)


@dataclass(slots=True)
class QdrantClientAdapter:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[4])
    _client: Any | None = None

    def _resolve_local_path(self) -> Path:
        raw = Path(CONTEXT_MEMORY_QDRANT_LOCAL_PATH)
        if raw.is_absolute():
            return raw
        return self.project_root / raw

    def get_client(self):
        if self._client is not None:
            return self._client

        from qdrant_client import QdrantClient

        if CONTEXT_MEMORY_QDRANT_MODE == "server":
            kwargs: dict[str, Any] = {"url": CONTEXT_MEMORY_QDRANT_URL}
            if CONTEXT_MEMORY_QDRANT_API_KEY:
                kwargs["api_key"] = CONTEXT_MEMORY_QDRANT_API_KEY
            self._client = QdrantClient(**kwargs)
            return self._client

        local_path = self._resolve_local_path()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        self._client = QdrantClient(path=str(local_path))
        return self._client