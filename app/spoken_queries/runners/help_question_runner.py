from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.live_listeners.primary_listener.wakeword_matcher import normalize_text
from app.system_support.system_runtime_state import (
    is_help_explain_capture_enabled,
    set_help_explain_capture,
)
from app.spoken_queries.runners.help_query_parser import parse_help_query
from app.spoken_queries.runners.request_text import get_request_text


APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
HELP_ROOT = APP_DIR / "system_support" / "HELP"


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _flatten_help_items(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                items.append(item)
        return items

    if isinstance(payload, dict):
        if "items" in payload and isinstance(payload["items"], list):
            for item in payload["items"]:
                if isinstance(item, dict):
                    items.append(item)
            return items

        if "sections" in payload and isinstance(payload["sections"], list):
            for item in payload["sections"]:
                if isinstance(item, dict):
                    items.append(item)
            return items

        if any(key in payload for key in ("title", "text", "short_answer", "aliases", "tags")):
            items.append(payload)

    return items


def _load_all_help_items() -> list[dict[str, Any]]:
    if not HELP_ROOT.exists():
        return []

    all_items: list[dict[str, Any]] = []

    for path in HELP_ROOT.rglob("*.json"):
        payload = _load_json_file(path)
        for item in _flatten_help_items(payload):
            item = dict(item)
            item["_source_path"] = str(path.relative_to(APP_DIR))
            all_items.append(item)

    return all_items


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _score_item(query: str, item: dict[str, Any]) -> int:
    query_norm = normalize_text(query)
    if not query_norm:
        return 0

    title = normalize_text(str(item.get("title", "")))
    short_answer = normalize_text(str(item.get("short_answer", "")))
    text = normalize_text(str(item.get("text", "")))

    aliases = [normalize_text(x) for x in _as_text_list(item.get("aliases"))]
    tags = [normalize_text(x) for x in _as_text_list(item.get("tags"))]
    related = [normalize_text(x) for x in _as_text_list(item.get("related"))]

    score = 0

    if query_norm == title:
        score += 100
    if query_norm in aliases:
        score += 90
    if query_norm in tags:
        score += 70
    if query_norm in related:
        score += 45

    if title and query_norm in title:
        score += 50
    if short_answer and query_norm in short_answer:
        score += 25
    if text and query_norm in text:
        score += 20

    query_words = set(query_norm.split())
    haystack_words = set(
        " ".join([title, short_answer, text, *aliases, *tags, *related]).split()
    )

    score += len(query_words & haystack_words) * 8

    return score


def _build_help_menu(items: list[dict[str, Any]]) -> str:
    capture_status = "ON" if is_help_explain_capture_enabled(PROJECT_ROOT) else "OFF"

    if not items:
        return (
            "HELP is empty right now. "
            "Add JSON files under app/system_support/HELP. "
            f"Help explain capture is {capture_status}."
        )

    examples: list[str] = []

    for item in items:
        for example in _as_text_list(item.get("examples")):
            if example not in examples:
                examples.append(example)
            if len(examples) >= 8:
                break
        if len(examples) >= 8:
            break

    if not examples:
        examples = [
            "HELP MENU",
            "HELP EXPLAIN ON",
            "HELP EXPLAIN OFF",
            "EXPLAIN HELP",
            "EXPLAIN MEMORY",
            "EXPLAIN LLM",
            "HELP TROUBLESHOOTING",
        ]

    return (
        f"HELP is ready. Help explain capture is {capture_status}. "
        f"Try: " + " | ".join(examples[:8])
    )


def _answer_from_item(item: dict[str, Any]) -> str:
    short_answer = str(item.get("short_answer") or "").strip()
    text = str(item.get("text") or "").strip()

    if short_answer and text:
        answer = f"{short_answer} {text}"
    else:
        answer = short_answer or text

    if not answer:
        title = str(item.get("title") or "").strip()
        if title:
            answer = title

    return answer or "I found that help topic, but it has no readable answer yet."




def _build_result(
    request: dict[str, Any],
    *,
    query_text: str,
    help_query_text: str,
    answer: str,
    meta: dict[str, Any],
    ok: bool = True,
    error_code: str = "",
) -> dict[str, Any]:
    flags = request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {}

    result: dict[str, Any] = {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": ok,
        "runner_name": "help_question_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": query_text,
        "help_query_text": help_query_text,
        "answer_text": answer,
        "speech_text": answer,
        "flags": flags,
        "meta": meta,
    }

    if error_code:
        result["error_code"] = error_code

    return result


def run_help_question(request: dict[str, Any]) -> dict[str, Any]:
    query_text = get_request_text(request)
    intent = parse_help_query(query_text)

    if intent.explain_capture_action == "on":
        set_help_explain_capture(PROJECT_ROOT, enabled=True)
        answer = "Help explain capture is ON. EXPLAIN questions now go to HELP."
        return _build_result(
            request,
            query_text=query_text,
            help_query_text=intent.cleaned_query,
            answer=answer,
            meta={
                "help_connected": True,
                "help_root": str(HELP_ROOT),
                "help_mode": "explain_capture_on",
                "help_explain_capture_enabled": True,
            },
        )

    if intent.explain_capture_action == "off":
        set_help_explain_capture(PROJECT_ROOT, enabled=False)
        answer = "Help explain capture is OFF. EXPLAIN can now go to normal question flow."
        return _build_result(
            request,
            query_text=query_text,
            help_query_text=intent.cleaned_query,
            answer=answer,
            meta={
                "help_connected": True,
                "help_root": str(HELP_ROOT),
                "help_mode": "explain_capture_off",
                "help_explain_capture_enabled": False,
            },
        )

    items = _load_all_help_items()

    if intent.is_menu_request:
        answer = _build_help_menu(items)
        return _build_result(
            request,
            query_text=query_text,
            help_query_text=intent.cleaned_query,
            answer=answer,
            meta={
                "help_connected": True,
                "help_root": str(HELP_ROOT),
                "help_items_loaded": len(items),
                "help_mode": "menu",
                "help_explain_capture_enabled": is_help_explain_capture_enabled(PROJECT_ROOT),
            },
        )

    scored = sorted(
        ((_score_item(intent.cleaned_query, item), item) for item in items),
        key=lambda pair: pair[0],
        reverse=True,
    )

    best_score = scored[0][0] if scored else 0
    best_item = scored[0][1] if scored and best_score > 0 else None

    if best_item:
        answer = _answer_from_item(best_item)
        meta = {
            "help_connected": True,
            "help_root": str(HELP_ROOT),
            "help_items_loaded": len(items),
            "help_mode": "search",
            "help_explain_capture_enabled": is_help_explain_capture_enabled(PROJECT_ROOT),
            "help_query": intent.cleaned_query,
            "best_score": best_score,
            "best_title": str(best_item.get("title", "")),
            "source_path": str(best_item.get("_source_path", "")),
        }
    else:
        answer = "I did not find help for that topic yet. Try: HELP MENU."
        meta = {
            "help_connected": True,
            "help_root": str(HELP_ROOT),
            "help_items_loaded": len(items),
            "help_mode": "not_found",
            "help_explain_capture_enabled": is_help_explain_capture_enabled(PROJECT_ROOT),
            "help_query": intent.cleaned_query,
        }

    return _build_result(
        request,
        query_text=query_text,
        help_query_text=intent.cleaned_query,
        answer=answer,
        meta=meta,
    )