from __future__ import annotations

import json
import time
from typing import Any
from uuid import uuid4

from app.live_listeners.shared.listener_paths import (
    LIVE_MOMENT_HISTORY_JSONL,
    ensure_listener_runtime_dirs,
)


def append_live_moment(
    *,
    source_event_ids: list[str],
    source_session_id: str,
    paragraph: str,
    intent_type: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_listener_runtime_dirs()

    record = {
        "event_id": f"live_moment_{uuid4().hex}",
        "ts": time.time(),
        "source": "administrative_listener",
        "source_event_ids": source_event_ids,
        "source_session_id": source_session_id,
        "paragraph": paragraph,
        "intent_type": intent_type,
        "metadata": metadata or {},
    }

    with LIVE_MOMENT_HISTORY_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record
