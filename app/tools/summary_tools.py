from __future__ import annotations


def summarize_lines(lines: list[str], max_items: int = 5) -> str:
    cleaned = [line.strip() for line in lines if line.strip()]
    if not cleaned:
        return ""

    trimmed = cleaned[:max_items]
    return "\n".join(f"- {line}" for line in trimmed)


def summarize_text_blocks(blocks: list[str], max_chars: int = 500) -> str:
    merged = " ".join(block.strip() for block in blocks if block.strip())
    merged = " ".join(merged.split())

    if len(merged) <= max_chars:
        return merged

    return merged[:max_chars].rstrip() + "..."