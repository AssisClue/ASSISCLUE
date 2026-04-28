from __future__ import annotations

import time
from typing import Any


def build_world_state(window: list[dict[str, Any]]) -> dict[str, Any]:
    latest = window[-1] if window else {}

    return {
        "updated_at": time.time(),
        "active_moment_count": len(window),
        "latest_intent_type": latest.get("intent_type", ""),
        "latest_source_session_id": latest.get("source_session_id", ""),
        "latest_paragraph": latest.get("paragraph", ""),
    }
