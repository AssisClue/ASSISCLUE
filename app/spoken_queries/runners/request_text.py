from __future__ import annotations

from typing import Any


def get_request_text(payload: dict[str, Any]) -> str:
    return str(
        payload.get("text", "")
        or payload.get("cleaned_text", "")
        or payload.get("transcript_text", "")
    ).strip()
