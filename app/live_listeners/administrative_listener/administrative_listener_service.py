from __future__ import annotations

import json
import time
from typing import Any

from app.live_listeners.shared.listener_paths import (
    ADMINISTRATIVE_LISTENER_CURSOR_JSON,
    ADMINISTRATIVE_LISTENER_STATUS_JSON,
    ASSEMBLED_TRANSCRIPT_JSONL,
    ensure_listener_runtime_dirs,
)
from app.live_listeners.shared.listener_record_utils import (
    get_record_event_id,
    get_record_session_id,
)
from app.live_listeners.shared.transcript_reader import TranscriptReader

from .administrative_command_bridge import detect_administrative_command
from .administrative_command_execution_guard import (
    AdministrativeCommandExecutionGuard,
)
from .administrative_command_router import route_administrative_command
from .administrative_listener_config import (
    ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS,
    ADMINISTRATIVE_EXECUTE_COMMANDS,
    ADMINISTRATIVE_LISTENER_NAME,
    ADMINISTRATIVE_LISTENER_POLL_SECONDS,
)
from .live_moment_writer import append_live_moment
from .moment_window_builder import MomentWindowBuilder
from .paragraph_builder import build_paragraph
from .present_intent_filter import detect_present_intent


def write_administrative_listener_status(state: str, **extra: Any) -> None:
    ensure_listener_runtime_dirs()

    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "listener": ADMINISTRATIVE_LISTENER_NAME,
        "updated_at": time.time(),
    }
    payload.update(extra)

    ADMINISTRATIVE_LISTENER_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class AdministrativeListenerService:
    def __init__(self) -> None:
        self.reader = TranscriptReader(
            transcript_path=ASSEMBLED_TRANSCRIPT_JSONL,
            cursor_path=ADMINISTRATIVE_LISTENER_CURSOR_JSON,
        )
        self.window_builder = MomentWindowBuilder()
        self.execution_guard = AdministrativeCommandExecutionGuard()
        self._window: list[dict[str, Any]] = []
        self._running = False

    def process_record(self, record: dict[str, Any]) -> dict[str, Any] | None:
        self._window = self.window_builder.build_window(self._window, record)

        paragraph = build_paragraph(self._window)
        if not paragraph:
            return None

        command_match = detect_administrative_command(paragraph)
        intent_type = detect_present_intent(paragraph)

        if intent_type == "ignore" and not command_match:
            return None

        source_event_ids = [
            get_record_event_id(item)
            for item in self._window
            if get_record_event_id(item)
        ]
        source_session_id = get_record_session_id(record)

        metadata: dict[str, Any] = {
            "window_size": len(self._window),
        }

        if command_match:
            metadata["administrative_command"] = command_match
            metadata["has_administrative_command"] = True
            metadata["administrative_action_name"] = str(command_match.get("action_name") or "").strip()
            metadata["administrative_is_browser_command"] = bool(command_match.get("is_browser_command", False))
            metadata["administrative_routing_hint"] = command_match.get("routing_hint", {})
            metadata["listener_execution_policy"] = "execute_when_enabled"

            should_execute = False
            execution_reason = "execution_disabled"

            if ADMINISTRATIVE_EXECUTE_COMMANDS:
                if bool(command_match.get("is_browser_command", False)):
                    if ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS:
                        should_execute = True
                        execution_reason = "browser_command_enabled"
                    else:
                        execution_reason = "browser_execution_disabled"
                else:
                    should_execute = True
                    execution_reason = "administrative_execution_enabled"

            guard_allowed, fingerprint = self.execution_guard.should_execute(
                command=command_match,
                source_session_id=source_session_id,
                source_event_ids=source_event_ids,
                paragraph=paragraph,
            )

            metadata["administrative_execution_fingerprint"] = fingerprint
            metadata["administrative_execution_guard_allowed"] = bool(guard_allowed)
            metadata["administrative_execution_reason"] = execution_reason

            if should_execute and guard_allowed:
                execution_result = route_administrative_command(command_match)
                metadata["administrative_execution_result"] = execution_result
                metadata["administrative_execution_ok"] = bool(execution_result.get("ok", False))
            else:
                metadata["administrative_execution_result"] = {
                    "ok": False,
                    "skipped": True,
                    "reason": "guard_blocked" if not guard_allowed else execution_reason,
                }
                metadata["administrative_execution_ok"] = False

            if intent_type == "ignore":
                intent_type = "context_only"

        live_moment = append_live_moment(
            source_event_ids=source_event_ids,
            source_session_id=source_session_id,
            paragraph=paragraph,
            intent_type=intent_type,
            metadata=metadata,
        )

        if command_match and bool(command_match.get("is_browser_command", False)):
            self._window = []

        return live_moment

    def run_forever(self) -> None:
        self._running = True

        write_administrative_listener_status("starting")

        try:
            write_administrative_listener_status("running")

            while self._running:
                records = self.reader.read_new_records()

                for record in records:
                    live_moment = self.process_record(record)
                    if not live_moment:
                        continue

                    metadata = live_moment.get("metadata", {}) if isinstance(live_moment.get("metadata", {}), dict) else {}
                    command_meta = metadata.get("administrative_command", {}) if isinstance(metadata.get("administrative_command", {}), dict) else {}
                    execution_meta = metadata.get("administrative_execution_result", {}) if isinstance(metadata.get("administrative_execution_result", {}), dict) else {}

                    write_administrative_listener_status(
                        "running",
                        last_event="live_moment_written",
                        last_live_moment_id=live_moment.get("event_id", ""),
                        last_intent_type=live_moment.get("intent_type", ""),
                        last_administrative_action_name=str(command_meta.get("action_name") or "").strip(),
                        last_administrative_execution_ok=bool(execution_meta.get("ok", False)),
                    )

                    print(json.dumps(live_moment, ensure_ascii=False), flush=True)

                time.sleep(ADMINISTRATIVE_LISTENER_POLL_SECONDS)

        except KeyboardInterrupt:
            write_administrative_listener_status("stopped", reason="keyboard_interrupt")

        except Exception as exc:
            write_administrative_listener_status(
                "error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

        finally:
            write_administrative_listener_status("stopped")

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    AdministrativeListenerService().run_forever()
