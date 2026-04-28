from __future__ import annotations

import os


CONTEXT_MEMORY_INDEX_BACKEND = os.getenv(
    "CONTEXT_MEMORY_INDEX_BACKEND",
    "json",
).strip().lower()

CONTEXT_MEMORY_QDRANT_MODE = os.getenv(
    "CONTEXT_MEMORY_QDRANT_MODE",
    "local",
).strip().lower()

CONTEXT_MEMORY_QDRANT_LOCAL_PATH = os.getenv(
    "CONTEXT_MEMORY_QDRANT_LOCAL_PATH",
    "runtime/qdrant/context_memory_db",
).strip()

CONTEXT_MEMORY_QDRANT_URL = os.getenv(
    "CONTEXT_MEMORY_QDRANT_URL",
    "http://127.0.0.1:6333",
).strip()

CONTEXT_MEMORY_QDRANT_API_KEY = os.getenv(
    "CONTEXT_MEMORY_QDRANT_API_KEY",
    "",
).strip()

CONTEXT_MEMORY_QDRANT_COLLECTION = os.getenv(
    "CONTEXT_MEMORY_QDRANT_COLLECTION",
    "context_memory",
).strip()

CONTEXT_MEMORY_QDRANT_VECTOR_SIZE = int(
    os.getenv("CONTEXT_MEMORY_QDRANT_VECTOR_SIZE", "256")
)

CONTEXT_MEMORY_QDRANT_DISTANCE = os.getenv(
    "CONTEXT_MEMORY_QDRANT_DISTANCE",
    "cosine",
).strip().lower()

CONTEXT_MEMORY_QDRANT_SCHEMA_VERSION = os.getenv(
    "CONTEXT_MEMORY_QDRANT_SCHEMA_VERSION",
    "1",
).strip()