from __future__ import annotations

import json
import time
from collections import deque
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.speech_service import prepare_tts_text, should_skip_tts


APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

DISPLAY_ACTION_RESULTS_JSONL = (
    RUNTIME_DIR / "display_actions" / "results" / "display_action_results.jsonl"
)
SPOKEN_QUERY_RESULTS_JSONL = (
    RUNTIME_DIR / "queues" / "spoken_queries" / "spoken_query_results.jsonl"
)




SPEECH_OUT_DIR = RUNTIME_DIR / "queues" / "speech_out"
SPEECH_QUEUE_JSONL = SPEECH_OUT_DIR / "speech_queue.jsonl"
SPOKEN_HISTORY_JSONL = SPEECH_OUT_DIR / "spoken_history.jsonl"
LATEST_TTS_JSON = SPEECH_OUT_DIR / "latest_tts.json"
PLAYBACK_STATE_JSON = RUNTIME_DIR / "state" / "speech_out" / "playback_state.json"
AUDIO_DIR = SPEECH_OUT_DIR / "audio"
STATUS_DIR = RUNTIME_DIR / "status" / "speech_out"
SPEECH_QUEUE_WRITER_STATUS_JSON = STATUS_DIR / "speech_queue_writer_status.json"

SPEECH_QUEUE_WRITER_NAME = "speech_queue_writer"
SPEECH_QUEUE_WRITER_POLL_SECONDS = 0.35


def ensure_speech_runtime_dirs() -> None:
    SPEECH_OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    PLAYBACK_STATE_JSON.parent.mkdir(parents=True, exist_ok=True)

    for path in (
        SPEECH_QUEUE_JSONL,
        SPOKEN_HISTORY_JSONL,
    ):
        if not path.exists():
            path.write_text("", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_new_jsonl_lines(path: Path, start_offset: int) -> list[tuple[str, int]]:
    if not path.exists():
        return []

    file_size = path.stat().st_size
    offset = max(0, int(start_offset or 0))
    if offset > file_size:
        # File was truncated/rotated; restart from the beginning so we don't
        # "jump to end" and miss fresh lines.
        offset = 0

    lines: list[tuple[str, int]] = []
    # Tolerate an accidental UTF-8 BOM at the very start of the file.
    # `utf-8-sig` strips BOM only at stream start (offset 0).
    encoding = "utf-8-sig" if offset == 0 else "utf-8"
    with path.open("r", encoding=encoding) as fh:
        fh.seek(offset)
        while True:
            line_start = fh.tell()
            raw = fh.readline()
            if raw == "":
                break
            if not raw.endswith("\n"):
                fh.seek(line_start)
                break
            lines.append((raw.rstrip("\r\n"), fh.tell()))

    return lines


def _has_source_result_id(path: Path, source_result_id: str, *, tail: int = 300) -> bool:
    if not source_result_id:
        return False
    if not path.exists():
        return False
    max_tail_bytes = 262144
    file_size = path.stat().st_size
    read_size = min(max_tail_bytes, file_size)
    with path.open("rb") as fh:
        if read_size > 0:
            fh.seek(file_size - read_size)
        data = fh.read()
    text = data.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    if read_size > 0 and file_size > read_size and lines:
        lines = lines[1:]
    if tail > 0:
        lines = lines[-tail:]
    for raw_line in lines:
        try:
            payload = json.loads(raw_line.lstrip("\ufeff"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        if str(payload.get("source_result_id", "")).strip() == source_result_id:
            return True
    return False


def _read_recent_source_result_ids(path: Path, *, tail: int = 300) -> list[str]:
    if not path.exists():
        return []

    max_tail_bytes = 262144
    file_size = path.stat().st_size
    read_size = min(max_tail_bytes, file_size)
    with path.open("rb") as fh:
        if read_size > 0:
            fh.seek(file_size - read_size)
        data = fh.read()

    text = data.decode("utf-8", errors="ignore")
    lines = text.splitlines()
    if read_size > 0 and file_size > read_size and lines:
        lines = lines[1:]
    if tail > 0:
        lines = lines[-tail:]

    source_result_ids: list[str] = []
    for raw_line in lines:
        try:
            payload = json.loads(raw_line.lstrip("\ufeff"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        source_result_id = str(payload.get("source_result_id", "")).strip()
        if source_result_id:
            source_result_ids.append(source_result_id)
    return source_result_ids



def load_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}

    return {}


def write_status(path: Path, service_name: str, state: str, **extra: Any) -> None:
    ensure_speech_runtime_dirs()

    current = load_status(path)
    payload: dict[str, Any] = {
        "ok": state != "error",
        "state": state,
        "service": service_name,
        "updated_at": time.time(),
        "last_processed_line_number": int(current.get("last_processed_line_number", 0) or 0),
        "display_last_processed_byte_offset": int(current.get("display_last_processed_byte_offset", 0) or 0),
        "spoken_last_processed_byte_offset": int(current.get("spoken_last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class SpeechQueueWriter:
    def __init__(self) -> None:
        self._running = False
        self._recent_source_result_ids: set[str] = set()
        self._recent_source_result_id_order: deque[str] = deque()
        self._recent_source_result_id_limit = 500

    def _remember_source_result_id(self, source_result_id: str) -> None:
        source_result_id = str(source_result_id or "").strip()
        if not source_result_id or source_result_id in self._recent_source_result_ids:
            return

        self._recent_source_result_ids.add(source_result_id)
        self._recent_source_result_id_order.append(source_result_id)

        while len(self._recent_source_result_id_order) > self._recent_source_result_id_limit:
            oldest = self._recent_source_result_id_order.popleft()
            self._recent_source_result_ids.discard(oldest)

    def _hydrate_recent_source_result_ids(self) -> None:
        self._recent_source_result_ids.clear()
        self._recent_source_result_id_order.clear()

        for path in (SPEECH_QUEUE_JSONL, SPOKEN_HISTORY_JSONL):
            for source_result_id in _read_recent_source_result_ids(path):
                self._remember_source_result_id(source_result_id)

    def _has_recent_source_result_id(self, source_result_id: str) -> bool:
        source_result_id = str(source_result_id or "").strip()
        if not source_result_id:
            return False
        return source_result_id in self._recent_source_result_ids

    def _get_resume_offsets(self) -> tuple[int, int, int, int]:
        status = load_status(SPEECH_QUEUE_WRITER_STATUS_JSON)
        try:
            display_offset = int(status.get("display_last_processed_line_number", 0) or 0)
        except Exception:
            display_offset = 0
        try:
            spoken_offset = int(status.get("spoken_last_processed_line_number", 0) or 0)
        except Exception:
            spoken_offset = 0
        try:
            display_byte_offset = int(status.get("display_last_processed_byte_offset", 0) or 0)
        except Exception:
            display_byte_offset = 0
        try:
            spoken_byte_offset = int(status.get("spoken_last_processed_byte_offset", 0) or 0)
        except Exception:
            spoken_byte_offset = 0
        return (
            max(0, display_offset),
            max(0, spoken_offset),
            max(0, display_byte_offset),
            max(0, spoken_byte_offset),
        )

    def _get_last_processed_line_number(self) -> int:
        status = load_status(SPEECH_QUEUE_WRITER_STATUS_JSON)
        try:
            return int(status.get("last_processed_line_number", 0) or 0)
        except Exception:
            return 0

    def _set_last_processed_line_number(self, line_number: int) -> None:
        status = load_status(SPEECH_QUEUE_WRITER_STATUS_JSON)
        status["ok"] = True
        status["state"] = "running"
        status["service"] = SPEECH_QUEUE_WRITER_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(line_number)
        SPEECH_QUEUE_WRITER_STATUS_JSON.write_text(
            json.dumps(status, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _parse_result_line(self, raw_line: str) -> dict[str, Any] | None:
        raw_line = raw_line.strip().lstrip("\ufeff")
        if not raw_line:
            return None

        try:
            payload = json.loads(raw_line)
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        return payload

    def process_result(self, result: dict[str, Any], *, source_type: str) -> dict[str, Any] | None:
        source_result_id = str(result.get("result_id", "")).strip()
        if self._has_recent_source_result_id(source_result_id):
            return None

        speech_text = str(result.get("speech_text", "")).strip()
        cleaned_spoken_text = prepare_tts_text(speech_text)

        if should_skip_tts(cleaned_spoken_text):
            return None

        meta: dict[str, Any] = {
            "ok": bool(result.get("ok", False)),
            "error_code": str(result.get("error_code", "")).strip(),
        }

        action_name = str(result.get("action_name", "")).strip()
        if action_name:
            meta["action_name"] = action_name

        runner_name = str(result.get("runner_name", "")).strip()
        if runner_name:
            meta["runner_name"] = runner_name

        return {
            "speech_id": f"spq_{uuid4().hex}",
            "ts": time.time(),
            "source_type": source_type,
            "source_event_id": str(result.get("source_event_id", "")).strip(),
            "source_result_id": source_result_id,
            "text": speech_text,
            "spoken_text": cleaned_spoken_text,
            "priority": "normal",
            "flags": result.get("flags", {}) if isinstance(result.get("flags", {}), dict) else {},
            "meta": meta,
        }




    def run_forever(self) -> None:
        ensure_speech_runtime_dirs()
        self._running = True
        self._hydrate_recent_source_result_ids()

        (
            last_processed_display,
            last_processed_spoken,
            display_byte_offset,
            spoken_byte_offset,
        ) = self._get_resume_offsets()
        write_status(
            SPEECH_QUEUE_WRITER_STATUS_JSON,
            SPEECH_QUEUE_WRITER_NAME,
            "starting",
            display_last_processed_line_number=last_processed_display,
            spoken_last_processed_line_number=last_processed_spoken,
            display_last_processed_byte_offset=display_byte_offset,
            spoken_last_processed_byte_offset=spoken_byte_offset,
        )

        try:
            write_status(
                SPEECH_QUEUE_WRITER_STATUS_JSON,
                SPEECH_QUEUE_WRITER_NAME,
                "running",
                display_last_processed_line_number=last_processed_display,
                spoken_last_processed_line_number=last_processed_spoken,
                display_last_processed_byte_offset=display_byte_offset,
                spoken_last_processed_byte_offset=spoken_byte_offset,
            )

            while self._running:
                new_display = read_new_jsonl_lines(DISPLAY_ACTION_RESULTS_JSONL, display_byte_offset)
                new_spoken = read_new_jsonl_lines(SPOKEN_QUERY_RESULTS_JSONL, spoken_byte_offset)

                did_work = False

                if new_display:
                    for raw_line, line_end_offset in new_display:
                        last_processed_display += 1
                        display_byte_offset = line_end_offset

                        result = self._parse_result_line(raw_line)
                        if not result:
                            write_status(
                                SPEECH_QUEUE_WRITER_STATUS_JSON,
                                SPEECH_QUEUE_WRITER_NAME,
                                "running",
                                last_result_id="",
                                last_enqueued_speech_id="",
                                display_last_processed_line_number=last_processed_display,
                                spoken_last_processed_line_number=last_processed_spoken,
                                display_last_processed_byte_offset=display_byte_offset,
                                spoken_last_processed_byte_offset=spoken_byte_offset,
                            )
                            continue

                        queue_item = self.process_result(result, source_type="display_action_result")
                        if queue_item is not None:
                            append_jsonl(SPEECH_QUEUE_JSONL, queue_item)
                            self._remember_source_result_id(str(queue_item.get("source_result_id", "")).strip())
                            print(json.dumps(queue_item, ensure_ascii=False), flush=True)

                        write_status(
                            SPEECH_QUEUE_WRITER_STATUS_JSON,
                            SPEECH_QUEUE_WRITER_NAME,
                            "running",
                            last_result_id=str(result.get("result_id", "")).strip(),
                            last_enqueued_speech_id="" if queue_item is None else str(queue_item.get("speech_id", "")).strip(),
                            display_last_processed_line_number=last_processed_display,
                            spoken_last_processed_line_number=last_processed_spoken,
                            display_last_processed_byte_offset=display_byte_offset,
                            spoken_last_processed_byte_offset=spoken_byte_offset,
                        )
                        did_work = True

                if new_spoken:
                    for raw_line, line_end_offset in new_spoken:
                        last_processed_spoken += 1
                        spoken_byte_offset = line_end_offset

                        result = self._parse_result_line(raw_line)
                        if not result:
                            write_status(
                                SPEECH_QUEUE_WRITER_STATUS_JSON,
                                SPEECH_QUEUE_WRITER_NAME,
                                "running",
                                last_result_id="",
                                last_enqueued_speech_id="",
                                display_last_processed_line_number=last_processed_display,
                                spoken_last_processed_line_number=last_processed_spoken,
                                display_last_processed_byte_offset=display_byte_offset,
                                spoken_last_processed_byte_offset=spoken_byte_offset,
                            )
                            continue

                        queue_item = self.process_result(result, source_type="spoken_query_result")
                        if queue_item is not None:
                            append_jsonl(SPEECH_QUEUE_JSONL, queue_item)
                            self._remember_source_result_id(str(queue_item.get("source_result_id", "")).strip())
                            print(json.dumps(queue_item, ensure_ascii=False), flush=True)

                        write_status(
                            SPEECH_QUEUE_WRITER_STATUS_JSON,
                            SPEECH_QUEUE_WRITER_NAME,
                            "running",
                            last_result_id=str(result.get("result_id", "")).strip(),
                            last_enqueued_speech_id="" if queue_item is None else str(queue_item.get("speech_id", "")).strip(),
                            display_last_processed_line_number=last_processed_display,
                            spoken_last_processed_line_number=last_processed_spoken,
                            display_last_processed_byte_offset=display_byte_offset,
                            spoken_last_processed_byte_offset=spoken_byte_offset,
                        )
                        did_work = True

                if not did_work:
                    time.sleep(SPEECH_QUEUE_WRITER_POLL_SECONDS)
                    continue

                time.sleep(SPEECH_QUEUE_WRITER_POLL_SECONDS)

        except KeyboardInterrupt:
            write_status(
                SPEECH_QUEUE_WRITER_STATUS_JSON,
                SPEECH_QUEUE_WRITER_NAME,
                "stopped",
                reason="keyboard_interrupt",
            )

        except Exception as exc:
            write_status(
                SPEECH_QUEUE_WRITER_STATUS_JSON,
                SPEECH_QUEUE_WRITER_NAME,
                "error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

        finally:
            write_status(SPEECH_QUEUE_WRITER_STATUS_JSON, SPEECH_QUEUE_WRITER_NAME, "stopped")



    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    SpeechQueueWriter().run_forever()
