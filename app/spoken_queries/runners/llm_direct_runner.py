from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.llm.llm_service import generate_text_response
from app.llm.llm_prompts import RICK_DIRECT_SYSTEM_PROMPT
from app.spoken_queries.runners.request_text import get_request_text

DIRECT_LLM_PREFIXES = [
    "lets talk about",
    "talk about",
    "use text",
    "use file",
    "ask",
    "think",
    "answer",
    "llm",
]

LEADING_WAKEWORDS = {
    "hey",
    "hello",
    "ok",
    "say",
    "assistant",
    "rick",
    "ai",
}

MAX_WORDS_DEFAULT = 22
SPEECH_MAX_CHARS_DEFAULT = 250
ACTIVE_BROWSER_TEXT_MAX_CHARS = 12000
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DIR = PROJECT_ROOT / "runtime"
LATEST_SAVED_TEXT_CONTEXT_JSON = RUNTIME_DIR / "browser" / "latest_saved_text_context.json"
TEMP_KNOWLEDGE_DIR = RUNTIME_DIR / "knowledge_library" / "parsed" / "temp"
FILE_HINT_FILLER_WORDS = {
    "a",
    "an",
    "the",
    "this",
    "that",
    "saved",
    "text",
    "file",
    "page",
    "about",
}


def _max_words() -> int:
    raw = str(os.getenv("SPOKEN_QUERY_MAX_WORDS", "")).strip()
    if not raw:
        return MAX_WORDS_DEFAULT
    try:
        return max(5, int(float(raw)))
    except Exception:
        return MAX_WORDS_DEFAULT


def _explicit_max_words() -> int | None:
    raw = str(os.getenv("SPOKEN_QUERY_MAX_WORDS", "")).strip()
    if not raw:
        return None
    try:
        return max(5, int(float(raw)))
    except Exception:
        return None


def _speech_max_chars() -> int:
    raw = str(os.getenv("SPOKEN_QUERY_SPEECH_MAX_CHARS", "")).strip()
    if not raw:
        return SPEECH_MAX_CHARS_DEFAULT
    try:
        return max(40, int(float(raw)))
    except Exception:
        return SPEECH_MAX_CHARS_DEFAULT


def _truncate_words(text: str, max_words: int, *, suffix: str = "...") -> str:
    cleaned = " ".join(str(text or "").strip().split())
    if max_words <= 0 or not cleaned:
        return cleaned
    words = cleaned.split(" ")
    if len(words) <= max_words:
        return cleaned
    return " ".join(words[:max_words]).rstrip(" ,.;:!?") + suffix


def make_speech_text(full_text: str, max_chars: int) -> str:
    cleaned = " ".join(str(full_text or "").strip().split())
    if not cleaned:
        return ""
    max_chars = int(max_chars or 0)
    if max_chars <= 0 or len(cleaned) <= max_chars:
        return cleaned

    suffix = "..."
    head = cleaned[:max_chars]

    cut = max(head.rfind("."), head.rfind("!"), head.rfind("?"))
    if cut != -1:
        trimmed = head[: cut + 1].rstrip().rstrip(" ,;:-")
        if trimmed:
            return trimmed

    budget = max(1, max_chars - len(suffix))
    head = cleaned[:budget]
    space = head.rfind(" ")
    trimmed = head[:space].rstrip() if space != -1 else head.rstrip()
    trimmed = trimmed.rstrip(" ,;:-")
    if not trimmed:
        trimmed = head.rstrip()
    return trimmed + suffix


def _normalize_prefix_text(text: str) -> str:
    cleaned = str(text or "").strip().lower()
    for ch in ",.?;:!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    words = cleaned.split()
    if words:
        if len(words) >= 2 and words[0] in {"hey", "hello", "ok", "say"} and words[1] in {"assistant", "rick"}:
            words = words[2:]
        elif words[0] in LEADING_WAKEWORDS:
            words = words[1:]
    return " ".join(words).strip()


def _strip_direct_prefix(text: str) -> str:
    cleaned = " ".join((text or "").strip().split())
    lowered = _normalize_prefix_text(cleaned)

    for prefix in DIRECT_LLM_PREFIXES:
        if lowered == prefix or lowered.startswith(prefix + " "):
                return lowered[len(prefix):].strip(" ,:.-")
    return cleaned


def _has_direct_prefix(text: str) -> bool:
    cleaned = _normalize_prefix_text(text)
    return any(cleaned == prefix or cleaned.startswith(prefix + " ") for prefix in DIRECT_LLM_PREFIXES)


def _file_hint_tokens(text: str) -> list[str]:
    cleaned = _normalize_prefix_text(text)
    for prefix in DIRECT_LLM_PREFIXES:
        if cleaned == prefix or cleaned.startswith(prefix + " "):
            cleaned = cleaned[len(prefix):].strip()
            break
    for ch in "_-/\\.,:?;!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    tokens = []
    for token in cleaned.split():
        token = token.strip()
        if len(token) < 2 or token in FILE_HINT_FILLER_WORDS:
            continue
        tokens.append(token)
    return tokens


def _write_active_saved_text_pointer(path: Path) -> None:
    pointer = {
        "ok": True,
        "kind": "browser_saved_text_context",
        "saved_path": str(path.relative_to(PROJECT_ROOT)),
        "filename": path.name,
        "chars": path.stat().st_size if path.exists() else 0,
        "url": "",
        "title": "",
        "source_action": "spoken_file_hint",
        "created_at": time.time(),
    }
    LATEST_SAVED_TEXT_CONTEXT_JSON.parent.mkdir(parents=True, exist_ok=True)
    LATEST_SAVED_TEXT_CONTEXT_JSON.write_text(json.dumps(pointer, indent=2, ensure_ascii=False), encoding="utf-8")


def _activate_temp_text_by_hint(text: str) -> str:
    tokens = _file_hint_tokens(text)
    if not tokens or not TEMP_KNOWLEDGE_DIR.exists():
        return ""

    best_path: Path | None = None
    best_score = -1
    for path in TEMP_KNOWLEDGE_DIR.glob("*.txt"):
        name_tokens = _file_hint_tokens(path.stem)
        if not name_tokens:
            continue
        score = sum(1 for token in tokens if token in name_tokens)
        if score <= 0:
            continue
        if score == len(tokens):
            score += 100
        if score > best_score:
            best_score = score
            best_path = path

    if best_path is None:
        return ""

    _write_active_saved_text_pointer(best_path)
    return str(best_path.resolve())


def _load_active_browser_saved_text() -> dict[str, Any]:
    if not LATEST_SAVED_TEXT_CONTEXT_JSON.exists():
        return {"context_text": "", "used": False, "path": "", "truncated": False}

    try:
        pointer = json.loads(LATEST_SAVED_TEXT_CONTEXT_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {"context_text": "", "used": False, "path": "", "truncated": False}

    if not isinstance(pointer, dict):
        return {"context_text": "", "used": False, "path": "", "truncated": False}

    raw_path = str(pointer.get("saved_path") or "").strip()
    if not raw_path:
        return {"context_text": "", "used": False, "path": "", "truncated": False}

    saved_path = Path(raw_path)
    if not saved_path.is_absolute():
        saved_path = PROJECT_ROOT / saved_path

    try:
        resolved_path = saved_path.resolve()
        runtime_root = RUNTIME_DIR.resolve()
    except Exception:
        return {"context_text": "", "used": False, "path": "", "truncated": False}

    if runtime_root not in resolved_path.parents and resolved_path != runtime_root:
        return {"context_text": "", "used": False, "path": str(resolved_path), "truncated": False}

    if not resolved_path.exists() or not resolved_path.is_file():
        return {"context_text": "", "used": False, "path": str(resolved_path), "truncated": False}

    try:
        text = resolved_path.read_text(encoding="utf-8")
    except Exception:
        return {"context_text": "", "used": False, "path": str(resolved_path), "truncated": False}

    truncated = len(text) > ACTIVE_BROWSER_TEXT_MAX_CHARS
    if truncated:
        text = text[:ACTIVE_BROWSER_TEXT_MAX_CHARS]

    header = (
        "Active browser saved text context.\n"
        f"Source file: {pointer.get('filename', resolved_path.name)}\n"
        f"Page title: {pointer.get('title', '')}\n"
        f"Page URL: {pointer.get('url', '')}\n\n"
    )
    return {
        "context_text": header + text,
        "used": bool(text.strip()),
        "path": str(resolved_path),
        "truncated": truncated,
    }


def run_llm_direct_question(request: dict[str, Any]) -> dict[str, Any]:
    query_text = get_request_text(request)
    used_direct_prefix = _has_direct_prefix(query_text)
    user_text = _strip_direct_prefix(query_text)

    if not user_text:
        answer = "Tell me what you want me to ask the model."
        return {
            "result_id": f"sqr_{uuid4().hex}",
            "ts": time.time(),
            "ok": False,
            "runner_name": "llm_direct_runner",
            "source_event_id": str(request.get("source_event_id", "")).strip(),
            "routed_event_id": str(request.get("routed_event_id", "")).strip(),
            "query_text": query_text,
            "answer_text": answer,
            "speech_text": answer,
            "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
            "error_code": "missing_llm_query",
            "meta": {
                "llm_direct": used_direct_prefix,
                "default_persona_llm": not used_direct_prefix,
                "prefix_stripped": used_direct_prefix,
            },
        }

    activated_temp_path = _activate_temp_text_by_hint(query_text)
    active_context = _load_active_browser_saved_text()

    llm_result = generate_text_response(
        user_text=user_text,
        context_text=str(active_context.get("context_text") or ""),
        system_prompt=RICK_DIRECT_SYSTEM_PROMPT,
        metadata={
            "source": "spoken_queries",
            "runner": "llm_direct_runner",
            "llm_direct": True,
        },
    )

    if not llm_result.ok:
        answer = "The model is not available right now."
        return {
            "result_id": f"sqr_{uuid4().hex}",
            "ts": time.time(),
            "ok": False,
            "runner_name": "llm_direct_runner",
            "source_event_id": str(request.get("source_event_id", "")).strip(),
            "routed_event_id": str(request.get("routed_event_id", "")).strip(),
            "query_text": query_text,
            "answer_text": answer,
            "speech_text": answer,
            "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
            "error_code": "llm_unavailable",
            "meta": {
                "llm_direct": used_direct_prefix,
                "default_persona_llm": not used_direct_prefix,
                "active_browser_saved_text_used": bool(active_context.get("used", False)),
                "active_browser_saved_text_path": str(active_context.get("path") or ""),
                "activated_temp_text_path": activated_temp_path,
                "truncated": bool(active_context.get("truncated", False)),
                "provider": llm_result.provider,
                "model_name": llm_result.model_name,
                "llm_error": llm_result.error,
            },
        }

    answer = str(llm_result.text or "").strip()
    speech = make_speech_text(answer, _speech_max_chars())
    explicit_max_words = _explicit_max_words()
    if explicit_max_words is not None:
        speech = _truncate_words(speech, explicit_max_words)

    return {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "runner_name": "llm_direct_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": user_text,
        "answer_text": answer,
        "speech_text": speech,
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "llm_direct": used_direct_prefix,
            "default_persona_llm": not used_direct_prefix,
            "active_browser_saved_text_used": bool(active_context.get("used", False)),
            "active_browser_saved_text_path": str(active_context.get("path") or ""),
            "activated_temp_text_path": activated_temp_path,
            "truncated": bool(active_context.get("truncated", False)),
            "provider": llm_result.provider,
            "model_name": llm_result.model_name,
        },
    }
