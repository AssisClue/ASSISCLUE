from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.display_actions.helpers.screenshot_paths import (
    DISPLAY_ACTION_RESULTS_JSONL,
    DISPLAY_ACTION_STATUS_JSON,
    ensure_display_action_runtime_dirs,
)
from app.system_support.runtime_jsonl import append_jsonl, read_new_runtime_jsonl_lines
from .display_action_runner_registry import get_display_action_runner


APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

ROUTER_RUNTIME_DIR = RUNTIME_DIR / "queues" / "router_dispatch"
ACTION_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "action_queue.jsonl"

DISPLAY_ACTION_POLL_SECONDS = 0.35
DISPLAY_ACTION_SERVICE_NAME = "display_action_runner"


def load_display_action_status() -> dict[str, Any]:
    if not DISPLAY_ACTION_STATUS_JSON.exists():
        return {}

    try:
        payload = json.loads(DISPLAY_ACTION_STATUS_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    return {}


def write_display_action_status(state: str, **extra: Any) -> None:
    ensure_display_action_runtime_dirs()

    current = load_display_action_status()
    payload: dict[str, Any] = {
        "ok": state != "error",
        "state": state,
        "service": DISPLAY_ACTION_SERVICE_NAME,
        "updated_at": time.time(),
        "last_processed_line_number": int(current.get("last_processed_line_number", 0) or 0),
        "last_processed_byte_offset": int(current.get("last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)

    DISPLAY_ACTION_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class DisplayActionRouter:
    def __init__(self) -> None:
        self._running = False
        self._status_cache: dict[str, Any] | None = None

    def _load_status_cache(self) -> dict[str, Any]:
        if self._status_cache is None:
            self._status_cache = load_display_action_status()
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status_cache()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = DISPLAY_ACTION_SERVICE_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(status.get("last_processed_line_number", 0) or 0)
        status["last_processed_byte_offset"] = int(status.get("last_processed_byte_offset", 0) or 0)
        status.update(extra)

    def _flush_status(self) -> None:
        ensure_display_action_runtime_dirs()
        status = self._load_status_cache()
        DISPLAY_ACTION_STATUS_JSON.write_text(
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
        raw_line = raw_line.lstrip("\ufeff").strip()
        if not raw_line:
            return None

        try:
            payload = json.loads(raw_line)
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        if str(payload.get("target_runner", "")).strip() != "display_actions":
            return None

        return payload

    def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        command = request.get("command", {}) if isinstance(request.get("command", {}), dict) else {}
        action_name = str(command.get("action_name", "")).strip()
        capability = request.get("capability", {}) if isinstance(request.get("capability", {}), dict) else {}

        runner = get_display_action_runner(action_name)
        if runner is None:
            return {
                "result_id": f"dres_{uuid4().hex}",
                "ts": time.time(),
                "ok": False,
                "action_name": action_name,
                "source_event_id": str(request.get("source_event_id", "")).strip(),
                "routed_event_id": str(request.get("routed_event_id", "")).strip(),
                "error_code": "unsupported_display_action",
                "analysis_text": "",
                "speech_text": "That display action is not supported yet.",
                "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
                "meta": {
                    "capability_id": str(capability.get("capability_id", "")).strip(),
                },
            }

        return runner(request)

    def run_forever(self) -> None:
        ensure_display_action_runtime_dirs()
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
                new_lines = read_new_runtime_jsonl_lines(ACTION_QUEUE_JSONL, current_byte_offset)

                if not new_lines:
                    time.sleep(DISPLAY_ACTION_POLL_SECONDS)
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
                            last_action_name="",
                            last_result_ok=False,
                        )
                        self._flush_status()
                        continue

                    result = self.process_request(request)
                    append_jsonl(DISPLAY_ACTION_RESULTS_JSONL, result)

                    self._set_last_processed_line_number(
                        current_line_number,
                        byte_offset=current_byte_offset,
                    )
                    self._update_status(
                        "running",
                        last_event_id=str(request.get("source_event_id", "")).strip(),
                        last_action_name=str(result.get("action_name", "")).strip(),
                        last_result_ok=bool(result.get("ok", False)),
                    )
                    self._flush_status()

                    print(json.dumps(result, ensure_ascii=False), flush=True)

                time.sleep(DISPLAY_ACTION_POLL_SECONDS)

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
    DisplayActionRouter().run_forever()
