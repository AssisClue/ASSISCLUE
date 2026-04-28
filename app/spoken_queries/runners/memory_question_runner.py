from __future__ import annotations

import time
from uuid import uuid4

from app.context_memory.services.context_memory_service import ContextMemoryService
from app.spoken_queries.runners.request_text import get_request_text
from app.spoken_queries.runners.memory_query_hint_parser import parse_memory_query_intent


def run_memory_question(request: dict) -> dict:
    query_text = get_request_text(request)
    memory_intent = parse_memory_query_intent(query_text)
    memory_query_text = memory_intent.cleaned_query or query_text
    flags = request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {}
    use_memory = bool(flags.get("use_memory", False))

    preferred = list(memory_intent.hint.preferred_sources or [])
    allow_implicit_lookup = preferred in (["personas"], ["user_spaces.help"])

    if not use_memory and not allow_implicit_lookup:
        answer = "I can't check memory unless you say use memory."
        meta = {
            "memory_connected": False,
            "use_memory": use_memory,
            "fallback_reason": "use_memory_not_requested",
        }
    else:
        try:
            memory_service = ContextMemoryService.create_default()
            memory_answer = memory_service.answer_memory_query(
                memory_query_text,
                hint=memory_intent.hint,
            )
        except Exception as exc:
            answer = "I tried to check memory, but memory is not available right now."
            meta = {
                "memory_connected": False,
                "use_memory": use_memory,
                "implicit_lookup": allow_implicit_lookup and not use_memory,
                "fallback_reason": "memory_unavailable",
                "memory_error": f"{type(exc).__name__}: {exc}",
            }
        else:
            if memory_answer.memory_hits > 0:
                answer = memory_answer.matches[0]
                if memory_intent.hint.preferred_sources == ["personas"]:
                    answer = f"I found this persona profile: {answer}"
            else:
                if memory_intent.hint.preferred_sources == ["personas"]:
                    answer = "I checked persona profiles, but I did not find a clear match for that yet."
                elif memory_intent.hint.preferred_sources == ["user_spaces.help"]:
                    answer = "I did not find help for that topic yet. Try: explicar menu."
                else:
                    answer = "I checked memory, but I did not find a clear match for that yet."
            meta = {
                "memory_connected": True,
                "use_memory": use_memory,
                "implicit_lookup": allow_implicit_lookup and not use_memory,
                "memory_hits": memory_answer.memory_hits,
                "summary_lines": memory_answer.summary_lines,
                "fallback_reason": memory_answer.fallback_reason,
                "preferred_sources": list(memory_intent.hint.preferred_sources),
                "source_key": memory_intent.source_key,
            }

    return {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "runner_name": "memory_question_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": query_text,
        "memory_query_text": memory_query_text,
        "answer_text": answer,
        "speech_text": answer,
        "flags": flags,
        "meta": meta,
    }
