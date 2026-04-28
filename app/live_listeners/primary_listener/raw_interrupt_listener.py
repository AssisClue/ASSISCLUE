from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from app.live_listeners.shared.listener_paths import ensure_listener_runtime_dirs
from app.live_listeners.shared.transcript_reader import TranscriptReader

from .command_matcher import match_command
from .primary_listener_event_builder import build_command_event
from .wakeword_matcher import has_wakeword, normalize_text, split_after_wakeword

APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

RAW_TRANSCRIPT_JSONL = RUNTIME_DIR / "sacred" / "live_transcript_raw.jsonl"
RAW_INTERRUPT_CURSOR_JSON = RUNTIME_DIR / "state" / "live_listeners" / "raw_interrupt_listener_cursor.json"
RAW_INTERRUPT_STATUS_JSON = RUNTIME_DIR / "status" / "raw_interrupt_listener_status.json"

ROUTER_RUNTIME_DIR = RUNTIME_DIR / "queues" / "router_dispatch"
ROUTER_INPUT_QUEUE_JSONL = ROUTER_RUNTIME_DIR / "router_input_queue.jsonl"

RAW_INTERRUPT_LISTENER_NAME = "raw_interrupt_listener"
RAW_INTERRUPT_POLL_SECONDS = 0.12
RAW_INTERRUPT_DEDUP_SECONDS = 0.8


def ensure_raw_interrupt_runtime() -> None:
    ensure_listener_runtime_dirs()
    ROUTER_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    if not ROUTER_INPUT_QUEUE_JSONL.exists():
        ROUTER_INPUT_QUEUE_JSONL.write_text("", encoding="utf-8")
    if not RAW_TRANSCRIPT_JSONL.exists():
        RAW_TRANSCRIPT_JSONL.write_text("", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def write_raw_interrupt_status(state: str, **extra: Any) -> None:
    ensure_raw_interrupt_runtime()

    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "listener": RAW_INTERRUPT_LISTENER_NAME,
        "updated_at": time.time(),
    }
    payload.update(extra)

    RAW_INTERRUPT_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class RawInterruptListener:
    def __init__(self) -> None:
        self.reader = TranscriptReader(
            transcript_path=RAW_TRANSCRIPT_JSONL,
            cursor_path=RAW_INTERRUPT_CURSOR_JSON,
        )
        self._running = False
        self._last_emitted_at = 0.0
        self._last_emitted_text = ""

    def _build_interrupt_event(self, record: dict[str, Any]) -> dict[str, Any] | None:
        text = normalize_text(str(record.get("text", "") or ""))
        if not text:
            return None

        matched_wakeword, tail_text = split_after_wakeword(text)

        if matched_wakeword and tail_text:
            command = match_command(tail_text, wakeword_found=True)
            if command is not None and str(command.get("action_name", "")).strip() == "stop_talking":
                return build_command_event(
                    record,
                    matched_wakeword=matched_wakeword,
                    text=tail_text,
                    command_match=command,
                    flags={"use_memory": False},
                )

        command = match_command(text, wakeword_found=has_wakeword(text))
        if command is not None and str(command.get("action_name", "")).strip() == "stop_talking":
            return build_command_event(
                record,
                matched_wakeword="",
                text=text,
                command_match=command,
                flags={"use_memory": False},
            )

        return None

    def _emit_event(self, event: dict[str, Any]) -> None:
        append_jsonl(ROUTER_INPUT_QUEUE_JSONL, event)
        print(json.dumps(event, ensure_ascii=False), flush=True)

    def run_forever(self) -> None:
        self._running = True
        write_raw_interrupt_status("starting")

        try:
            write_raw_interrupt_status("running")

            while self._running:
                records = self.reader.read_new_records()

                for record in records:
                    event = self._build_interrupt_event(record)
                    if not event:
                        continue

                    now = time.time()
                    event_text = normalize_text(
                        str(event.get("cleaned_text", "") or event.get("text", "") or "")
                    )

                    if event_text == self._last_emitted_text and (now - self._last_emitted_at) < RAW_INTERRUPT_DEDUP_SECONDS:
                        write_raw_interrupt_status(
                            "running",
                            last_event="dedup_interrupt",
                            last_text=event_text,
                        )
                        continue

                    self._last_emitted_at = now
                    self._last_emitted_text = event_text
                    self._emit_event(event)

                    write_raw_interrupt_status(
                        "running",
                        last_event="interrupt_emitted",
                        last_event_id=str(event.get("event_id", "")).strip(),
                        last_source_event_id=str(record.get("event_id", "")).strip(),
                        last_text=event_text,
                    )

                time.sleep(RAW_INTERRUPT_POLL_SECONDS)

        except KeyboardInterrupt:
            write_raw_interrupt_status("stopped", reason="keyboard_interrupt")
        except Exception as exc:
            write_raw_interrupt_status(
                "error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        finally:
            write_raw_interrupt_status("stopped")

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    RawInterruptListener().run_forever()
