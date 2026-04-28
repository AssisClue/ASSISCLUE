from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.system_support.commands.command_service import run_command
from app.system_support.runtime_jsonl import append_jsonl, read_new_runtime_jsonl_lines

from .route_event_builder import build_routed_event
from .route_rules import resolve_route
from .schemas.queue_target_schema import (
    QUEUE_TARGET_ACTION,
    QUEUE_TARGET_IGNORE,
    QUEUE_TARGET_RESPONSE,
)


APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

ROUTER_RUNTIME_DIR = RUNTIME_DIR / "queues" / "router_dispatch"
ROUTER_INPUT_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "router_input_queue.jsonl"
ACTION_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "action_queue.jsonl"
RESPONSE_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "response_queue.jsonl"
ROUTER_STATUS_JSON = RUNTIME_DIR / "status" / "router_dispatch" / "router_status.json"

ROUTER_NAME = "router_dispatch"
ROUTER_POLL_SECONDS = 0.35


def ensure_router_runtime_dirs() -> None:
    ROUTER_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    ROUTER_STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)

    for path in (
        ROUTER_INPUT_QUEUE_JSONL,
        ACTION_QUEUE_JSONL,
        RESPONSE_QUEUE_JSONL,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def load_router_status() -> dict[str, Any]:
    if not ROUTER_STATUS_JSON.exists():
        return {}

    try:
        payload = json.loads(ROUTER_STATUS_JSON.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    return {}


def write_router_status(state: str, **extra: Any) -> None:
    ensure_router_runtime_dirs()

    current = load_router_status()
    payload: dict[str, Any] = {
        "ok": state != "error",
        "state": state,
        "service": ROUTER_NAME,
        "updated_at": time.time(),
        "last_processed_line_number": int(current.get("last_processed_line_number", 0) or 0),
        "last_processed_byte_offset": int(current.get("last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)

    ROUTER_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class RouterService:
    def __init__(self) -> None:
        self._running = False
        self._status_cache: dict[str, Any] | None = None

    def _load_status_cache(self) -> dict[str, Any]:
        if self._status_cache is None:
            self._status_cache = load_router_status()
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status_cache()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = ROUTER_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(status.get("last_processed_line_number", 0) or 0)
        status["last_processed_byte_offset"] = int(status.get("last_processed_byte_offset", 0) or 0)
        status.update(extra)

    def _flush_status(self) -> None:
        ensure_router_runtime_dirs()
        status = self._load_status_cache()
        ROUTER_STATUS_JSON.write_text(
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

    def _parse_event_line(self, raw_line: str) -> dict[str, Any] | None:
        raw_line = raw_line.lstrip("\ufeff").strip()
        if not raw_line:
            return None

        try:
            payload = json.loads(raw_line)
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        return payload

    def _write_to_target_queue(self, target_queue: str, payload: dict[str, Any]) -> None:
        if target_queue == QUEUE_TARGET_ACTION:
            append_jsonl(ACTION_QUEUE_JSONL, payload)
            return

        if target_queue == QUEUE_TARGET_RESPONSE:
            append_jsonl(RESPONSE_QUEUE_JSONL, payload)
            return

    def _run_command_core_if_needed(self, event: dict[str, Any], routed_event: dict[str, Any]) -> None:
        if str(event.get("event_type", "")).strip() != "primary_command":
            return

        command = event.get("command", {}) if isinstance(event.get("command", {}), dict) else {}
        if not isinstance(command.get("command_core"), dict):
            return

        command_text = str(event.get("text", "") or "").strip()
        if not command_text:
            command_text = str(event.get("cleaned_text", "") or "").strip()

        result = run_command(command_text)
        routed_event["command_result"] = asdict(result)

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        route = resolve_route(event)
        routed_event = build_routed_event(
            event,
            target_queue=route["target_queue"],
            target_runner=route["target_runner"],
            routing_reason=route["routing_reason"],
        )

        self._run_command_core_if_needed(event, routed_event)

        if route["target_queue"] != QUEUE_TARGET_IGNORE:
            self._write_to_target_queue(route["target_queue"], routed_event)

        return routed_event

    def run_forever(self) -> None:
        ensure_router_runtime_dirs()
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
                new_lines = read_new_runtime_jsonl_lines(ROUTER_INPUT_QUEUE_JSONL, current_byte_offset)

                if not new_lines:
                    time.sleep(ROUTER_POLL_SECONDS)
                    continue

                last_event_id = ""
                last_route = ""
                last_routing_reason = ""

                for raw_line, line_end_offset in new_lines:
                    current_line_number += 1
                    current_byte_offset = line_end_offset

                    event = self._parse_event_line(raw_line)
                    if not event:
                        self._set_last_processed_line_number(
                            current_line_number,
                            byte_offset=current_byte_offset,
                        )
                        last_event_id = ""
                        last_route = "invalid_jsonl_line"
                        last_routing_reason = ""
                        self._update_status(
                            "running",
                            last_event_id=last_event_id,
                            last_route=last_route,
                            last_routing_reason=last_routing_reason,
                        )
                        self._flush_status()
                        continue

                    routed_event = self.process_event(event)

                    self._set_last_processed_line_number(
                        current_line_number,
                        byte_offset=current_byte_offset,
                    )
                    last_event_id = str(event.get("event_id", "")).strip()
                    last_route = str(routed_event.get("target_queue", "")).strip()
                    last_routing_reason = str(routed_event.get("routing_reason", "")).strip()
                    self._update_status(
                        "running",
                        last_event_id=last_event_id,
                        last_route=last_route,
                        last_routing_reason=last_routing_reason,
                        last_command_status=(
                            str(
                                (
                                    routed_event.get("command_result", {})
                                    if isinstance(routed_event.get("command_result", {}), dict)
                                    else {}
                                ).get("status", "")
                            ).strip()
                        ),
                    )
                    self._flush_status()

                    print(json.dumps(routed_event, ensure_ascii=False), flush=True)

                time.sleep(ROUTER_POLL_SECONDS)

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
    RouterService().run_forever()
