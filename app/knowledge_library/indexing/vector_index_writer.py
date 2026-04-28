from __future__ import annotations


class VectorIndexWriter:
    def write_chunks(self, *, chunks: list[dict], write_vectors: bool = False) -> dict:
        return {
            "write_vectors": bool(write_vectors),
            "vector_backend": "none",
            "written_count": 0,
            "status": "skipped" if not write_vectors else "not_connected_yet",
        }