from __future__ import annotations

from .context_runner_config import SUMMARY_MAX_CHARS


def build_summary(paragraphs: list[str]) -> str:
    merged = " ".join(part.strip() for part in paragraphs if part and part.strip())
    merged = " ".join(merged.split())

    if len(merged) <= SUMMARY_MAX_CHARS:
        return merged

    return merged[: SUMMARY_MAX_CHARS - 3].rstrip() + "..."