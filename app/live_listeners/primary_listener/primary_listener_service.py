from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from app.live_listeners.shared.listener_paths import (
    ASSEMBLED_TRANSCRIPT_JSONL,
    PRIMARY_LISTENER_CURSOR_JSON,
    PRIMARY_LISTENER_STATUS_JSON,
    ensure_listener_runtime_dirs,
)
from app.live_listeners.shared.listener_record_utils import get_record_text
from app.live_listeners.shared.transcript_reader import TranscriptReader
from app.personas.services.persona_service import PersonaService
from app.system_support.system_runtime_state import read_system_runtime_state
from app.system_support.system_runtime_state import set_edit_mode

from .command_matcher import match_command
from .matcher_vocabulary import looks_like_strong_no_wakeword_question
from .memory_flag_matcher import detect_use_memory_flag, strip_memory_flag_phrases
from .primary_listener_config import EDIT_MODE_ALIASES, PRIMARY_LISTENER_NAME, PRIMARY_LISTENER_POLL_SECONDS
from .primary_listener_event_builder import (
    build_command_event,
    build_quick_question_event,
    build_wakeword_only_event,
)
from .quick_question_matcher import (
    looks_like_quick_question,
    looks_like_spoken_question,
    looks_like_useful_request,
)
from .wakeword_matcher import (
    has_wakeword,
    normalize_text,
    split_after_wakeword,
)

APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

ROUTER_RUNTIME_DIR = RUNTIME_DIR / "queues" / "router_dispatch"
ROUTER_INPUT_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "router_input_queue.jsonl"
PLAYBACK_STATE_JSON = RUNTIME_DIR / "state" / "speech_out" / "playback_state.json"

PLAYBACK_ECHO_COOLDOWN_SECONDS = float(os.getenv("PLAYBACK_ECHO_COOLDOWN_SECONDS", "2.0"))
PLAYBACK_ECHO_TEXT_IGNORE_SECONDS = float(os.getenv("PLAYBACK_ECHO_TEXT_IGNORE_SECONDS", "8.0"))


def ensure_primary_router_runtime() -> None:
    ROUTER_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if not ROUTER_INPUT_QUEUE_JSONL.exists():
        ROUTER_INPUT_QUEUE_JSONL.write_text("", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _playback_echo_guard_active(now_ts: float | None = None) -> bool:
    if not PLAYBACK_STATE_JSON.exists():
        return False

    now = float(now_ts or time.time())
    try:
        playback_mtime = float(PLAYBACK_STATE_JSON.stat().st_mtime)
    except Exception:
        playback_mtime = 0.0

    try:
        payload = json.loads(PLAYBACK_STATE_JSON.read_text(encoding="utf-8-sig"))
    except Exception:
        return bool(playback_mtime) and (now - playback_mtime) <= PLAYBACK_ECHO_COOLDOWN_SECONDS

    if not isinstance(payload, dict):
        return bool(playback_mtime) and (now - playback_mtime) <= PLAYBACK_ECHO_COOLDOWN_SECONDS

    status = str(payload.get("status", "")).strip().lower()
    if status in {"playing", "synthesizing"}:
        return True

    def coerce_float(value: object) -> float:
        try:
            return float(value or 0.0)
        except Exception:
            return 0.0

    until_ts = coerce_float(payload.get("until_ts"))
    if until_ts > 0.0 and now <= (until_ts + PLAYBACK_ECHO_COOLDOWN_SECONDS):
        return True

    updated_at = coerce_float(payload.get("updated_at"))
    if updated_at > 0.0 and now <= (updated_at + PLAYBACK_ECHO_COOLDOWN_SECONDS):
        return True

    return False


def _strip_repeated_wakeword_prefix(text: str, *, max_passes: int = 2) -> str:
    cleaned = normalize_text(text)
    for _ in range(max_passes):
        matched, tail = split_after_wakeword(cleaned)
        if not matched or not tail:
            break
        cleaned = tail
    return cleaned


def _recent_spoken_text_guard_active(transcript_text: str, now_ts: float | None = None) -> bool:
    block_window = float(PLAYBACK_ECHO_TEXT_IGNORE_SECONDS or 0.0)
    if block_window <= 0.0:
        return False

    if not PLAYBACK_STATE_JSON.exists():
        return False

    now = float(now_ts or time.time())
    try:
        payload = json.loads(PLAYBACK_STATE_JSON.read_text(encoding="utf-8-sig"))
    except Exception:
        return False

    if not isinstance(payload, dict):
        return False

    spoken_text = str(payload.get("spoken_text", "") or "").strip()
    if not spoken_text:
        return False

    def coerce_float(value: object) -> float:
        try:
            return float(value or 0.0)
        except Exception:
            return 0.0

    last_ts = max(
        coerce_float(payload.get("until_ts")),
        coerce_float(payload.get("updated_at")),
        coerce_float(payload.get("started_at")),
        coerce_float(payload.get("ts")),
    )
    if last_ts <= 0.0 or now > (last_ts + block_window):
        return False

    heard = normalize_text(_strip_repeated_wakeword_prefix(transcript_text))
    spoken = normalize_text(spoken_text)

    if not heard or not spoken:
        return False

    return heard == spoken


def _build_command_match_candidates(text: str, *, window_words: int = 15) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    candidates: list[str] = []

    def add_candidate(value: str) -> None:
        candidate = normalize_text(value)
        if candidate and candidate not in candidates:
            candidates.append(candidate)

    add_candidate(normalized)
    add_candidate(" ".join(normalized.split()[:window_words]))
    add_candidate(strip_memory_flag_phrases(normalized))
    add_candidate(strip_memory_flag_phrases(" ".join(normalized.split()[:window_words])))
    return candidates


def _match_command_candidates(text: str, *, wakeword_found: bool) -> dict[str, Any] | None:
    for candidate in _build_command_match_candidates(text):
        match = match_command(candidate, wakeword_found=wakeword_found)
        if match:
            return match
    return None


def _looks_like_browser_control_phrase(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False

    browser_prefixes = (
        "browser ",
        "open browser",
        "start browser",
        "launch browser",
        "open url",
        "open website",
        "go to website",
        "go to url",
        "search ",
        "search for ",
        "look for ",
        "find on web ",
        "search web for ",
        "click ",
        "click on ",
        "click text ",
        "type ",
        "press ",
        "hit ",
        "scroll down",
        "scroll up",
        "page down",
        "page up",
        "new tab",
    )
    return any(normalized == prefix.strip() or normalized.startswith(prefix) for prefix in browser_prefixes)


def _resolve_active_persona() -> str:
    payload = read_system_runtime_state(PROJECT_ROOT) or {}
    persona_id = str(payload.get("active_persona") or "rick").strip()
    return persona_id or "rick"


def _is_edit_mode_phrase(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False
    return normalized in {normalize_text(alias) for alias in EDIT_MODE_ALIASES if normalize_text(alias)}


def write_primary_listener_status(state: str, **extra: Any) -> None:
    ensure_listener_runtime_dirs()
    ensure_primary_router_runtime()

    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "listener": PRIMARY_LISTENER_NAME,
        "updated_at": time.time(),
    }
    payload.update(extra)

    PRIMARY_LISTENER_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class PrimaryListenerService:
    def __init__(self) -> None:
        self.reader = TranscriptReader(
            transcript_path=ASSEMBLED_TRANSCRIPT_JSONL,
            cursor_path=PRIMARY_LISTENER_CURSOR_JSON,
        )
        self._persona_service = PersonaService(PROJECT_ROOT / "app" / "personas" / "profiles")
        self._persona_policy_cache = {
            "persona_id": "",
            "assistant_directed_default": False,
            "loaded_at": 0.0,
        }
        self._persona_policy_ttl_seconds = 1.5
        self._running = False

    def _is_assistant_directed_by_default(self) -> bool:
        now = time.time()
        if (now - float(self._persona_policy_cache["loaded_at"])) < self._persona_policy_ttl_seconds:
            return bool(self._persona_policy_cache["assistant_directed_default"])

        persona_id = _resolve_active_persona()
        assistant_directed_default = self._persona_service.is_assistant_directed_by_default(persona_id)
        self._persona_policy_cache = {
            "persona_id": persona_id,
            "assistant_directed_default": assistant_directed_default,
            "loaded_at": now,
        }
        return assistant_directed_default

    def _write_debug_status(
        self,
        record: dict[str, Any],
        *,
        reason: str,
        event_type: str = "",
        cleaned_text: str = "",
        matched_wakeword: str = "",
        use_memory: bool = False,
        decision: str = "ignored",
    ) -> None:
        write_primary_listener_status(
            "running",
            last_event="primary_event_detected" if decision == "emitted" else "primary_event_ignored",
            last_event_id="",
            last_source_event_id=record.get("event_id", ""),
            last_detected_event_type=event_type,
            last_text=record.get("text", ""),
            last_cleaned_text=cleaned_text,
            last_debug_reason=reason,
            last_decision=decision,
            last_wakeword_found=bool(matched_wakeword),
            last_matched_wakeword=matched_wakeword,
            last_use_memory=bool(use_memory),
        )

    def process_record(self, record: dict[str, Any]) -> dict[str, Any] | None:
        text = get_record_text(record)
        if not text:
            self._write_debug_status(record, reason="empty_transcript_text")
            return None

        normalized_text = normalize_text(text)
        if not normalized_text:
            self._write_debug_status(record, reason="empty_after_normalize")
            return None

        if _playback_echo_guard_active():
            self._write_debug_status(record, reason="anti_echo_blocked")
            return None

        if _recent_spoken_text_guard_active(normalized_text):
            self._write_debug_status(record, reason="anti_echo_text_blocked", cleaned_text=normalized_text)
            return None

        assistant_directed_default = self._is_assistant_directed_by_default()
        wakeword_found = has_wakeword(normalized_text)
        matched_wakeword, tail_text = split_after_wakeword(normalized_text)

        if not matched_wakeword:
            if _is_edit_mode_phrase(normalized_text):
                set_edit_mode(PROJECT_ROOT, active=True)
                self._write_debug_status(
                    record,
                    reason="edit_mode_enabled",
                    cleaned_text=normalized_text,
                    decision="emitted",
                )
                return None

            use_memory = detect_use_memory_flag(normalized_text)
            flags = {"use_memory": use_memory}

            if _looks_like_browser_control_phrase(normalized_text):
                self._write_debug_status(
                    record,
                    reason="browser_command_deferred_to_administrative_listener",
                    cleaned_text=normalized_text,
                )
                return None

            no_wakeword_command = _match_command_candidates(normalized_text, wakeword_found=False)
            if no_wakeword_command:
                return build_command_event(
                    record,
                    matched_wakeword="",
                    text=normalized_text,
                    command_match=no_wakeword_command,
                    flags=flags,
                )

            is_question = looks_like_quick_question(normalized_text) or looks_like_spoken_question(normalized_text)

            if assistant_directed_default and (is_question or flags["use_memory"]):
                return build_quick_question_event(
                    record,
                    matched_wakeword="",
                    text=normalized_text,
                    flags=flags,
                )

            if is_question and looks_like_strong_no_wakeword_question(normalized_text, max_words=14):
                return build_quick_question_event(
                    record,
                    matched_wakeword="",
                    text=normalized_text,
                    flags=flags,
                )

            self._write_debug_status(
                record,
                reason="no_wakeword",
                cleaned_text=normalized_text,
                use_memory=use_memory,
            )
            return None

        semantic_text = _strip_repeated_wakeword_prefix(tail_text or normalized_text)

        if not semantic_text:
            self._write_debug_status(
                record,
                reason="primary_wakeword_only",
                event_type="primary_wakeword_only",
                cleaned_text=normalized_text,
                matched_wakeword=matched_wakeword,
            )
            return None

        if _is_edit_mode_phrase(semantic_text):
            set_edit_mode(PROJECT_ROOT, active=True)
            self._write_debug_status(
                record,
                reason="edit_mode_enabled",
                cleaned_text=semantic_text,
                matched_wakeword=matched_wakeword,
                decision="emitted",
            )
            return None

        flags = {
            "use_memory": detect_use_memory_flag(semantic_text),
        }

        if _looks_like_browser_control_phrase(semantic_text):
            self._write_debug_status(
                record,
                reason="browser_command_deferred_to_administrative_listener",
                cleaned_text=semantic_text,
                matched_wakeword=matched_wakeword,
            )
            return None

        command = _match_command_candidates(semantic_text, wakeword_found=wakeword_found)
        if command:
            return build_command_event(
                record,
                matched_wakeword=matched_wakeword,
                text=semantic_text,
                command_match=command,
                flags=flags,
            )

        if looks_like_quick_question(semantic_text) or looks_like_spoken_question(semantic_text):
            return build_quick_question_event(
                record,
                matched_wakeword=matched_wakeword,
                text=semantic_text,
                flags=flags,
            )

        if looks_like_useful_request(semantic_text):
            return build_quick_question_event(
                record,
                matched_wakeword=matched_wakeword,
                text=semantic_text,
                flags=flags,
            )

        return build_wakeword_only_event(
            record,
            matched_wakeword=matched_wakeword,
            text=semantic_text,
            flags=flags,
        )

    def _emit_event(self, event: dict[str, Any]) -> None:
        ensure_primary_router_runtime()
        append_jsonl(ROUTER_INPUT_QUEUE_JSONL, event)
        print(json.dumps(event, ensure_ascii=False), flush=True)

    def run_forever(self) -> None:
        self._running = True
        write_primary_listener_status("starting")

        try:
            write_primary_listener_status("running")

            while self._running:
                records = self.reader.read_new_records()

                for record in records:
                    event = self.process_record(record)
                    if not event:
                        continue

                    self._emit_event(event)

                    self._write_debug_status(
                        record,
                        reason=str(event.get("event_type", "")).strip() or "primary_event_detected",
                        event_type=str(event.get("event_type", "")).strip(),
                        cleaned_text=str(event.get("cleaned_text", "")).strip(),
                        matched_wakeword=str(event.get("matched_wakeword", "")).strip(),
                        use_memory=bool((event.get("flags", {}) or {}).get("use_memory", False)),
                        decision="emitted",
                    )
                    write_primary_listener_status(
                        "running",
                        last_event_id=event.get("event_id", ""),
                    )

                time.sleep(PRIMARY_LISTENER_POLL_SECONDS)

        except KeyboardInterrupt:
            write_primary_listener_status("stopped", reason="keyboard_interrupt")
        except Exception as exc:
            write_primary_listener_status(
                "error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        finally:
            write_primary_listener_status("stopped")

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    PrimaryListenerService().run_forever()
