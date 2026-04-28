from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.spoken_queries.matchers.simple_question_matcher import match_simple_question
from app.spoken_queries.runners.request_text import get_request_text
from app.system_support.system_runtime_state import read_system_runtime_state


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_system_mode() -> str:
    payload = read_system_runtime_state(_project_root()) or {}
    mode = str(payload.get("active_mode") or payload.get("system_mode") or "").strip()
    return mode or "unknown"


def run_simple_question(request: dict[str, Any]) -> dict[str, Any]:
    query_text = get_request_text(request)
    match = match_simple_question(query_text)

    if not match:
        return {
            "result_id": f"sqr_{uuid4().hex}",
            "ts": time.time(),
            "ok": False,
            "runner_name": "simple_question_runner",
            "source_event_id": str(request.get("source_event_id", "")).strip(),
            "routed_event_id": str(request.get("routed_event_id", "")).strip(),
            "query_text": query_text,
            "answer_text": "",
            "speech_text": "I can't answer that as a simple question yet.",
            "error_code": "simple_question_not_supported",
            "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
            "meta": {},
        }

    intent = match["intent"]

    if intent == "current_time":
        answer = f"It is {datetime.now().strftime('%I:%M %p').lstrip('0')}."
    elif intent == "current_date":
        answer = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    elif intent == "presence_check":
        answer = "Yes, I'm here."
    elif intent == "system_mode_unknown":
        mode = _resolve_system_mode()
        answer = f"The current mode is {mode}."
    elif intent == "identity":
        answer = "I'm your assistant voice pipeline."
    else:
        answer = "I can't answer that as a simple question yet."

    return {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "runner_name": "simple_question_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": query_text,
        "answer_text": answer,
        "speech_text": answer,
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "intent": intent,
        },
    }
