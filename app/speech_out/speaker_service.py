from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

from app.config import AppConfig
from app.settings.tts_settings import TTSSettings

from .speech_queue_writer import (
    AUDIO_DIR,
    LATEST_TTS_JSON,
    PLAYBACK_STATE_JSON,
    SPEECH_QUEUE_JSONL,
    SPOKEN_HISTORY_JSONL,
    STATUS_DIR,
    ensure_speech_runtime_dirs,
)
from .tts_bridge import synthesize_and_play_speech


SPEAKER_STATUS_JSON = STATUS_DIR / "speaker_status.json"
SPEAKER_SERVICE_NAME = "speaker_service"
SPEAKER_POLL_SECONDS = 0.35
STOP_REQUEST_JSON = PLAYBACK_STATE_JSON.parent / "stop_request.json"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_jsonl_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    # Tolerate an accidental UTF-8 BOM at the very start of the file.
    return path.read_text(encoding="utf-8-sig").splitlines()


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
        "last_processed_byte_offset": int(current.get("last_processed_byte_offset", 0) or 0),
    }
    payload.update(extra)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


class SpeakerService:
    def __init__(self) -> None:
        self._running = False
        self._config = AppConfig.build(Path(__file__).resolve().parents[2])
        self._tts_settings = TTSSettings()
        self._status_cache: dict[str, Any] | None = None
        self._stop_watch_last_ts = 0.0
        self._stop_watch_thread: threading.Thread | None = None
        self._interrupt_until_ts = 0.0
        self._tts_active = False

    def _reset_stale_playback_state_on_start(self) -> None:
        if not PLAYBACK_STATE_JSON.exists():
            return
        now = time.time()
        try:
            payload = json.loads(PLAYBACK_STATE_JSON.read_text(encoding="utf-8-sig"))
        except Exception:
            return
        if not isinstance(payload, dict):
            return
        status = str(payload.get("status", "")).strip().lower()
        if status not in {"playing", "synthesizing"}:
            return
        try:
            updated_at = float(payload.get("updated_at", 0.0) or 0.0)
        except Exception:
            updated_at = 0.0
        try:
            until_ts = float(payload.get("until_ts", 0.0) or 0.0)
        except Exception:
            until_ts = 0.0
        stale = (updated_at > 0.0 and (now - updated_at) > 20.0) or (until_ts > 0.0 and now > (until_ts + 2.0))
        if not stale:
            return
        payload.update({"status": "idle", "updated_at": now, "stale_reset": True})
        try:
            PLAYBACK_STATE_JSON.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _start_stop_watch(self) -> None:
        if self._stop_watch_thread is not None:
            return

        def watch() -> None:
            while self._running:
                try:
                    if STOP_REQUEST_JSON.exists():
                        try:
                            payload = json.loads(STOP_REQUEST_JSON.read_text(encoding="utf-8"))
                        except Exception:
                            payload = {}
                        if not isinstance(payload, dict):
                            payload = {}
                        try:
                            ts = float(payload.get("ts", 0.0) or 0.0)
                        except Exception:
                            ts = 0.0
                        if ts > self._stop_watch_last_ts:
                            self._stop_watch_last_ts = ts
                            self._interrupt_until_ts = time.time() + 8.0

                        # One-time use:
                        # - If audio is currently playing, let tts_bridge see the file and stop playback,
                        #   then tts_bridge will delete it.
                        # - If nothing is playing, delete it immediately so it can't affect future audio.
                        if not bool(self._tts_active):
                            try:
                                STOP_REQUEST_JSON.unlink()
                            except Exception:
                                pass
                except Exception:
                    pass
                time.sleep(0.08)

        self._stop_watch_thread = threading.Thread(target=watch, name="speaker_stop_watch", daemon=True)
        self._stop_watch_thread.start()

    def _load_status_cache(self) -> dict[str, Any]:
        if self._status_cache is None:
            self._status_cache = load_status(SPEAKER_STATUS_JSON)
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status_cache()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = SPEAKER_SERVICE_NAME
        status["updated_at"] = time.time()
        status["last_processed_line_number"] = int(status.get("last_processed_line_number", 0) or 0)
        status["last_processed_byte_offset"] = int(status.get("last_processed_byte_offset", 0) or 0)
        status.update(extra)

    def _flush_status(self) -> None:
        ensure_speech_runtime_dirs()
        status = self._load_status_cache()
        SPEAKER_STATUS_JSON.write_text(
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

    def _parse_queue_line(self, raw_line: str) -> dict[str, Any] | None:
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

    def process_queue_item(self, item: dict[str, Any]) -> dict[str, Any]:
        speech_id = str(item.get("speech_id", "")).strip()
        output_path = AUDIO_DIR / f"{speech_id}.wav"

        self._tts_active = True
        try:
            tts_record = synthesize_and_play_speech(
                config=self._config,
                tts_settings=self._tts_settings,
                text=str(item.get("text", "")).strip(),
                output_path=output_path,
                latest_tts_path=LATEST_TTS_JSON,
                playback_state_path=PLAYBACK_STATE_JSON,
            )
        finally:
            self._tts_active = False

        spoken_record = {
            "speech_id": speech_id,
            "ts": time.time(),
            "source_type": str(item.get("source_type", "")).strip(),
            "source_event_id": str(item.get("source_event_id", "")).strip(),
            "source_result_id": str(item.get("source_result_id", "")).strip(),
            "text": str(item.get("text", "")).strip(),
            "spoken_text": str(tts_record.get("spoken_text", "")).strip(),
            "output_path": str(tts_record.get("output_path", "")).strip(),
            "status": str(tts_record.get("status", "")).strip(),
            "backend": str(tts_record.get("backend", "")).strip(),
            "voice": str(tts_record.get("voice", "")).strip(),
            "lang_code": str(tts_record.get("lang_code", "")).strip(),
            "sample_rate": tts_record.get("sample_rate"),
            "duration_seconds": tts_record.get("duration_seconds"),
            "elapsed_seconds": tts_record.get("elapsed_seconds"),
            "playback_result": tts_record.get("playback_result", {}),
            "flags": item.get("flags", {}) if isinstance(item.get("flags", {}), dict) else {},
            "meta": item.get("meta", {}) if isinstance(item.get("meta", {}), dict) else {},
        }
        return spoken_record

    def run_forever(self) -> None:
        ensure_speech_runtime_dirs()
        self._running = True
        self._reset_stale_playback_state_on_start()
        self._start_stop_watch()

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
                new_lines = read_new_jsonl_lines(SPEECH_QUEUE_JSONL, current_byte_offset)

                if not new_lines:
                    time.sleep(SPEAKER_POLL_SECONDS)
                    continue

                for raw_line, line_end_offset in new_lines:
                    if time.time() < float(self._interrupt_until_ts or 0.0):
                        break
                    current_line_number += 1
                    current_byte_offset = line_end_offset

                    item = self._parse_queue_line(raw_line)
                    if not item:
                        self._set_last_processed_line_number(
                            current_line_number,
                            byte_offset=current_byte_offset,
                        )
                        self._update_status(
                            "running",
                            last_speech_id="",
                            last_status="invalid_jsonl_line",
                        )
                        self._flush_status()
                        continue

                    spoken_record = self.process_queue_item(item)
                    append_jsonl(SPOKEN_HISTORY_JSONL, spoken_record)

                    self._set_last_processed_line_number(
                        current_line_number,
                        byte_offset=current_byte_offset,
                    )
                    self._update_status(
                        "running",
                        last_speech_id=str(item.get("speech_id", "")).strip(),
                        last_status=str(spoken_record.get("status", "")).strip(),
                    )
                    self._flush_status()

                    print(json.dumps(spoken_record, ensure_ascii=False), flush=True)

                time.sleep(SPEAKER_POLL_SECONDS)

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
    SpeakerService().run_forever()
