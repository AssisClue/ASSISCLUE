from __future__ import annotations

import os
import shutil
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    qdrant_path = project_root / "runtime" / "qdrant" / "test_context_memory_db"

    if qdrant_path.exists():
        shutil.rmtree(qdrant_path, ignore_errors=True)

    os.environ["CONTEXT_MEMORY_INDEX_BACKEND"] = "qdrant"
    os.environ["CONTEXT_MEMORY_QDRANT_MODE"] = "local"
    os.environ["CONTEXT_MEMORY_QDRANT_LOCAL_PATH"] = str(qdrant_path)
    os.environ["CONTEXT_MEMORY_QDRANT_COLLECTION"] = "test_context_memory"

    from app.context_memory.backends.qdrant.qdrant_index_sync_service import QdrantIndexSyncService
    from app.context_memory.backends.qdrant.qdrant_memory_index import QdrantMemoryIndex
    from app.context_memory.backends.qdrant.qdrant_search_adapter import QdrantSearchAdapter

    sync_service = QdrantIndexSyncService(collection_name="test_context_memory")
    rebuild = sync_service.rebuild_from_json()
    assert rebuild["ok"] is True
    assert rebuild["collection_name"] == "test_context_memory"

    index = QdrantMemoryIndex(collection_name="test_context_memory", sync_service=sync_service)
    search = QdrantSearchAdapter(qdrant_memory_index=index)

    results = search.search_text(query="test", limit=3)
    assert isinstance(results, list)

    status = sync_service.read_index_status()
    assert isinstance(status, dict)
    assert status.get("index_backend") == "qdrant"

    print("test_qdrant_local_backend=ok")


if __name__ == "__main__":
    main()