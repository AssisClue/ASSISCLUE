from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.personas.services.persona_service import PersonaService
from app.system_support.runtime_jsonl import (
    append_jsonl,
    append_runtime_jsonl,
    build_chat_history_item,
    read_new_runtime_jsonl_lines,
)
from app.spoken_queries.matchers.help_query_matcher import is_help_query
from app.spoken_queries.matchers.memory_required_matcher import requires_memory_runner
from app.spoken_queries.matchers.simple_question_matcher import match_simple_question
from app.spoken_queries.runners.help_question_runner import run_help_question
from app.spoken_queries.runners.memory_question_runner import run_memory_question
from app.spoken_queries.runners.simple_question_runner import run_simple_question
from app.spoken_queries.runners.simple_refusal_runner import run_simple_refusal
from app.spoken_queries.runners.llm_direct_runner import run_llm_direct_question
from app.spoken_queries.runners.request_text import get_request_text


APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
CHAT_HISTORY_JSONL = RUNTIME_DIR / "output" / "chat_history.jsonl"

ROUTER_RUNTIME_DIR = RUNTIME_DIR / "queues" / "router_dispatch"
RESPONSE_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "response_queue.jsonl"

SPOKEN_QUERIES_QUEUE_DIR = RUNTIME_DIR / "queues" / "spoken_queries"
STATUS_DIR = RUNTIME_DIR / "status" / "spoken_queries"

SPOKEN_QUERY_RESULTS_JSONL = SPOKEN_QUERIES_QUEUE_DIR / "spoken_query_results.jsonl"
SPOKEN_QUERY_STATUS_JSON = STATUS_DIR / "spoken_query_status.json"

SPOKEN_QUERY_ROUTER_NAME = "spoken_query_router"
SPOKEN_QUERY_POLL_SECONDS = 0.35


def ensure_spoken_query_runtime_dirs() -> None:
    SPOKEN_QUERIES_QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)

    if not SPOKEN_QUERY_RESULTS_JSONL.exists():
        SPOKEN_QUERY_RESULTS_JSONL.write_text("", encoding="utf-8")


DIRECT_LLM_PREFIXES = (
    "ask rick",
    "rick think",
    "rick answer",
    "use llm",
    "lets talk about",
    "talk about",
    "use text",
    "use file",
    "think",
)


def _is_direct_llm_request(text: str) -> bool:
    cleaned = str(text or "").strip().lower()
    for ch in ",.?;:!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    normalized = " ".join(cleaned.split())

    words = normalized.split()
    if words:
        if len(words) >= 2 and words[0] in {"hey", "ok", "hello", "say"} and words[1] in {"assistant", "rick"}:
            normalized = " ".join(words[2:])
        elif words[0] in {"hey", "ok", "hello", "say", "assistant", "rick", "ai"}:
            normalized = " ".join(words[1:])

    return any(normalized.startswith(prefix) for prefix in DIRECT_LLM_PREFIXES)


def _run_command_core_result(request: dict[str, Any]) -> dict[str, Any] | None:
    command = request.get("command", {}) if isinstance(request.get("command", {}), dict) else {}
    if str(command.get("action_name", "")).strip() != "command_core":
        return None

    command_result = request.get("command_result", {})
    if not isinstance(command_result, dict):
        return None

    message = str(command_result.get("message", "") or "").strip()
    if not message:
        status = str(command_result.get("status", "") or "").strip()
        if status == "confirmation_required":
            message = "Confirmation is required to execute that command."
        elif bool(command_result.get("ok", False)):
            message = "Command executed."
        else:
            message = "Command failed."

    errors = command_result.get("errors", [])
    first_error = ""
    if isinstance(errors, list):
        for item in errors:
            cleaned = str(item or "").strip()
            if cleaned:
                first_error = cleaned
                break

    return {
        "result_id": f"sqr_{uuid4().hex}",
        "ts": time.time(),
        "ok": bool(command_result.get("ok", False)),
        "runner_name": "command_core_runner",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "query_text": get_request_text(request),
        "answer_text": message,
        "speech_text": message,
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "error_code": "" if bool(command_result.get("ok", False)) else (first_error or "command_execution_failed"),
        "meta": {
            "command_status": str(command_result.get("status", "")).strip(),
            "command_action": str(command_result.get("action", "")).strip(),
            "command_target": str(command_result.get("target", "")).strip(),
            "requires_confirmation": bool(command_result.get("requires_confirmation", False)),
            "command_errors": errors if isinstance(errors, list) else [],
        },
    }


def load_status() -> dict[str, Any]:
    if not SPOKEN_QUERY_STATUS_JSON.exists():
        return {}

    try:
        payload = json.loads(SPOKEN_QUERY_STATUS_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}

    return {}


def write_spoken_query_status(state: str, **extra: Any) -> None:
    ensure_spoken_query_runtime_dirs()

    current = load_status()
    payload: dict[str, Any] = {
        "ok": state != "error",
        "state": state,
        "service": SPOKEN_QUERY_ROUTER_NAME,
        "updated_at": time.time(),
        "last_processed_line_number": int(current.get("last_processed_line_number", 0) or 0),
        "last_processed_byte_offset": int(current.get("last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)

    SPOKEN_QUERY_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class SpokenQueryRouter:
    def __init__(self) -> None:
        self._running = False
        self._status_cache: dict[str, Any] | None = None
        self._persona_service = PersonaService(PROJECT_ROOT / "app" / "personas" / "profiles")
        self._persona_policy_cache = {
            "assistant_directed_default": False,
            "persona_id": "",
            "loaded_at": 0.0,
        }
        self._persona_policy_ttl_seconds = 1.5

    def _load_status_cache(self) -> dict[str, Any]:
        if self._status_cache is None:
            self._status_cache = load_status()
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status_cache()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = SPOKEN_QUERY_ROUTER_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(status.get("last_processed_line_number", 0) or 0)
        status["last_processed_byte_offset"] = int(status.get("last_processed_byte_offset", 0) or 0)
        status.update(extra)

    def _flush_status(self) -> None:
        ensure_spoken_query_runtime_dirs()
        status = self._load_status_cache()
        SPOKEN_QUERY_STATUS_JSON.write_text(
            json.dumps(status, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _get_last_processed_line_number(self) -> int:
        status = self._load_status_cache()
        try:
            return int(status.get("last_processed_line_number", 0) or 0)
        except Exception:
            return 0

    def _get_last_processed_byte_offset(self) -> int:
        status = self._load_status_cache()
        try:
            return int(status.get("last_processed_byte_offset", 0) or 0)
        except Exception:
            return 0

    def _set_last_processed_line_number(self, line_number: int, *, byte_offset: int) -> None:
        self._update_status(
            "running",
            last_processed_line_number=int(line_number),
            last_processed_byte_offset=max(0, int(byte_offset or 0)),
        )

    def _parse_request_line(self, raw_line: str) -> dict[str, Any] | None:
        raw_line = raw_line.strip().lstrip("\ufeff")
        if not raw_line:
            return None

        try:
            payload = json.loads(raw_line)
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        if str(payload.get("target_runner", "")).strip() != "spoken_queries":
            return None

        return payload

    def _should_use_default_llm_for_active_persona(self) -> bool:
        now = time.time()
        cached_age = now - float(self._persona_policy_cache.get("loaded_at", 0.0) or 0.0)
        if cached_age < self._persona_policy_ttl_seconds:
            return bool(self._persona_policy_cache.get("assistant_directed_default", False))

        persona_id = self._persona_service.get_active_persona_id(PROJECT_ROOT)
        assistant_directed_default = self._persona_service.is_assistant_directed_by_default(persona_id)
        self._persona_policy_cache = {
            "assistant_directed_default": assistant_directed_default,
            "persona_id": persona_id,
            "loaded_at": now,
        }
        return assistant_directed_default

    def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        command_result = _run_command_core_result(request)
        if command_result is not None:
            return command_result

        query_text = get_request_text(request)
        flags = request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {}
        event_type = str(request.get("event_type", "")).strip()

        if _is_direct_llm_request(query_text):
            return run_llm_direct_question(request)

        if is_help_query(query_text):
            return run_help_question(request)

        if requires_memory_runner(query_text, flags=flags):
            return run_memory_question(request)

        if match_simple_question(query_text):
            return run_simple_question(request)

        if (
            event_type == "primary_quick_question"
            and self._should_use_default_llm_for_active_persona()
        ):
            return run_llm_direct_question(request)

        return run_simple_refusal(request)

    def run_forever(self) -> None:
        ensure_spoken_query_runtime_dirs()
        self._running = True

        self._update_status("starting")
        self._flush_status()

        try:
            self._update_status("running")
            self._flush_status()

            current_line_number = self._get_last_processed_line_number()
            current_byte_offset = self._get_last_processed_byte_offset()
            if current_line_number < 0:
                current_line_number = 0

            while self._running:
                new_lines = read_new_runtime_jsonl_lines(
                    RESPONSE_QUEUE_JSONL,
                    current_byte_offset,
                    bom_at_start=True,
                )

                if not new_lines:
                    time.sleep(SPOKEN_QUERY_POLL_SECONDS)
                    continue

                for raw_line, line_end_offset in new_lines:
                    current_line_number += 1
                    current_byte_offset = line_end_offset

                    request = self._parse_request_line(raw_line)
                    if not request:
                        self._set_last_processed_line_number(
                            current_line_number,
                            byte_offset=current_byte_offset,
                        )
                        self._update_status(
                            "running",
                            last_event_id="",
                            last_runner_name="",
                            last_result_ok=False,
                            last_debug_reason="spoken_invalid_jsonl_line",
                        )
                        self._flush_status()
                        continue

                    result = self.process_request(request)
                    append_jsonl(SPOKEN_QUERY_RESULTS_JSONL, result)

                    try:
                        persona_id = self._persona_service.get_active_persona_id(PROJECT_ROOT)
                    except Exception:
                        persona_id = ""

                    try:
                        user_text = get_request_text(request)
                        if user_text:
                            append_runtime_jsonl(
                                CHAT_HISTORY_JSONL,
                                build_chat_history_item(
                                    "user",
                                    user_text,
                                    persona=persona_id,
                                    source="spoken_query_user",
                                ),
                            )

                        answer_text = str(result.get("answer_text", "") or "").strip()
                        if answer_text:
                            meta = result.get("meta", {}) if isinstance(result.get("meta", {}), dict) else {}
                            append_runtime_jsonl(
                                CHAT_HISTORY_JSONL,
                                build_chat_history_item(
                                    "assistant",
                                    answer_text,
                                    persona=persona_id,
                                    model_name=str(meta.get("model_name", "") or ""),
                                    source="spoken_query_assistant",
                                ),
                            )
                    except Exception:
                        pass

                    self._set_last_processed_line_number(
                        current_line_number,
                        byte_offset=current_byte_offset,
                    )

                    last_runner_name = str(result.get("runner_name", "")).strip()
                    self._update_status(
                        "running",
                        last_event_id=str(request.get("source_event_id", "")).strip(),
                        last_runner_name=last_runner_name,
                        last_result_ok=bool(result.get("ok", False)),
                        last_debug_reason=(
                            str(result.get("error_code", "")).strip()
                            or str(
                                (result.get("meta", {}) if isinstance(result.get("meta", {}), dict) else {}).get(
                                    "fallback_reason",
                                    "",
                                )
                            ).strip()
                            or last_runner_name
                        ),
                    )
                    self._flush_status()

                    print(json.dumps(result, ensure_ascii=False), flush=True)

                time.sleep(SPOKEN_QUERY_POLL_SECONDS)

        except KeyboardInterrupt:
            self._update_status("stopped", reason="keyboard_interrupt")
            self._flush_status()

        except Exception as exc:
            self._update_status("error", error=f"{type(exc).__name__}: {exc}")
            self._flush_status()
            raise

        finally:
            self._update_status("stopped")
            self._flush_status()

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    SpokenQueryRouter().run_forever()
