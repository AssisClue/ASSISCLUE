from __future__ import annotations


class ParagraphLocator:
    def find(
        self,
        *,
        text: str,
        query: str,
        limit: int = 3,
        max_chars_per_result: int = 500,
    ) -> list[dict]:
        clean_query = str(query or "").strip().lower()
        if not clean_query:
            return []

        paragraphs = [part.strip() for part in str(text or "").split("\n\n") if part.strip()]
        results: list[dict] = []

        for idx, para in enumerate(paragraphs):
            if clean_query not in para.lower():
                continue

            snippet = para[:max_chars_per_result] if max_chars_per_result > 0 else para
            results.append(
                {
                    "paragraph_index": idx,
                    "text": snippet,
                    "match_query": clean_query,
                }
            )
            if len(results) >= max(1, int(limit)):
                break

        return results