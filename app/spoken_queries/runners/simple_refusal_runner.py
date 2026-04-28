from __future__ import annotations

import time
from uuid import uuid4

from app.spoken_queries.runners.request_text import get_request_text


def run_simple_refusal(request: dict) -> dict:
    query_text = get_request_text(request)

    answer = "I can't answer that yet."

    return {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "runner_name": "simple_refusal_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": query_text,
        "answer_text": answer,
        "speech_text": answer,
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {},
    }
