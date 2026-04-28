from __future__ import annotations

from typing import Any


def build_streaming_debug_payload(
    *,
    enabled: bool,
    last_partial_text: str,
    stable_counter: int,
    buffer_seconds: float,
) -> dict[str, Any]:
    return {
        "streaming_enabled": enabled,
        "streaming_last_partial_text": last_partial_text,
        "streaming_stable_counter": stable_counter,
        "streaming_buffer_seconds": round(buffer_seconds, 3),
    }