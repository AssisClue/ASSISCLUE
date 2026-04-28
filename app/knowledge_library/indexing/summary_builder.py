from __future__ import annotations


class SummaryBuilder:
    def build_summary(self, text: str, max_summary_chars: int = 800) -> str:
        clean = str(text or "").strip()
        if not clean:
            return ""

        paragraphs = [p.strip() for p in clean.split("\n\n") if p.strip()]
        if not paragraphs:
            return clean[:max_summary_chars]

        picked: list[str] = []
        total = 0

        for para in paragraphs[:4]:
            if total >= max_summary_chars:
                break
            space_left = max_summary_chars - total
            piece = para[:space_left].strip()
            if piece:
                picked.append(piece)
                total += len(piece) + 2

        return "\n\n".join(picked).strip()