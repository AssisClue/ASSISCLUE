from __future__ import annotations


class TextChunker:
    def chunk_text(self, text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[dict]:
        clean = str(text or "")
        if not clean.strip():
            return []

        size = max(100, int(chunk_size))
        overlap = max(0, min(int(chunk_overlap), size - 1))

        chunks: list[dict] = []
        start = 0
        idx = 0

        while start < len(clean):
            end = min(len(clean), start + size)
            piece = clean[start:end].strip()
            if piece:
                chunks.append(
                    {
                        "chunk_index": idx,
                        "start_index": start,
                        "end_index": end,
                        "text": piece,
                    }
                )
                idx += 1
            if end >= len(clean):
                break
            start = max(start + 1, end - overlap)

        return chunks