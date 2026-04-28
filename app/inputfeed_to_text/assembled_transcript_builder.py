from __future__ import annotations

import json
import time
from typing import Any

from .inputfeed_settings import (
    ASSEMBLER_FLUSH_IDLE_SECONDS,
    ASSEMBLER_MAX_BUFFER_PARTS,
    ASSEMBLER_MERGE_WINDOW_SECONDS,
    LIVE_TRANSCRIPT_RAW_JSONL,
)
from .transcript_runtime import (
    append_assembled_transcript_line,
    ensure_runtime_dirs,
    write_assembled_status,
)

POLL_SECONDS = 0.25


def _normalize_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def _extract_text(record: dict[str, Any]) -> str:
    for key in ("text", "transcript_text", "cleaned_text", "final_text", "raw_text"):
        text = _normalize_text(str(record.get(key, "") or ""))
        if text:
            return text
    return ""


def _extract_ts(record: dict[str, Any]) -> float:
    try:
        return float(record.get("ts", 0) or 0)
    except Exception:
        return 0.0


def _read_new_jsonl_lines(path, start_offset: int) -> list[tuple[str, int]]:
    if not path.exists():
        return []

    file_size = path.stat().st_size
    offset = max(0, int(start_offset or 0))
    if offset > file_size:
        offset = file_size

    lines: list[tuple[str, int]] = []
    with path.open("r", encoding="utf-8") as fh:
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


class AssembledTranscriptBuilder:
    def __init__(self) -> None:
        self._running = False
        self._buffer: list[dict[str, Any]] = []
        self._byte_offset = 0
        self._last_seen_at = time.time()

    def _should_merge(self, record: dict[str, Any]) -> bool:
        if not self._buffer:
            return True

        prev = self._buffer[-1]
        prev_ts = _extract_ts(prev)
        curr_ts = _extract_ts(record)

        if prev_ts <= 0 or curr_ts <= 0:
            return len(self._buffer) < ASSEMBLER_MAX_BUFFER_PARTS

        return (
            (curr_ts - prev_ts) <= ASSEMBLER_MERGE_WINDOW_SECONDS
            and len(self._buffer) < ASSEMBLER_MAX_BUFFER_PARTS
        )

    def _flush_buffer(self) -> None:
        if not self._buffer:
            return

        parts = [_extract_text(item) for item in self._buffer]
        text = _normalize_text(" ".join(part for part in parts if part))
        if not text:
            self._buffer = []
            return

        first = self._buffer[0]
        last = self._buffer[-1]

        append_assembled_transcript_line(
            session_id=str(last.get("session_id", "") or first.get("session_id", "")).strip(),
            text=text,
            source_event_ids=[
                str(item.get("event_id", "")).strip()
                for item in self._buffer
                if str(item.get("event_id", "")).strip()
            ],
            start_ts=_extract_ts(first),
            end_ts=_extract_ts(last),
            part_count=len(self._buffer),
        )
        self._buffer = []

    def _process_record(self, record: dict[str, Any]) -> None:
        text = _extract_text(record)
        if not text:
            return

        if self._should_merge(record):
            self._buffer.append(record)
            return

        self._flush_buffer()
        self._buffer.append(record)

    def run_forever(self) -> None:
        ensure_runtime_dirs()
        if LIVE_TRANSCRIPT_RAW_JSONL.exists():
            try:
                self._byte_offset = int(LIVE_TRANSCRIPT_RAW_JSONL.stat().st_size)
            except Exception:
                self._byte_offset = 0
        self._running = True
        write_assembled_status("starting", last_processed_byte_offset=self._byte_offset)

        try:
            write_assembled_status("running", last_processed_byte_offset=self._byte_offset)

            while self._running:
                new_lines = _read_new_jsonl_lines(LIVE_TRANSCRIPT_RAW_JSONL, self._byte_offset)

                if new_lines:
                    for raw_line, line_end_offset in new_lines:
                        self._byte_offset = line_end_offset
                        try:
                            record = json.loads(raw_line)
                        except Exception:
                            write_assembled_status(
                                "running",
                                last_processed_byte_offset=self._byte_offset,
                                last_error="invalid_json",
                            )
                            continue

                        if isinstance(record, dict):
                            self._process_record(record)
                            self._last_seen_at = time.time()

                        write_assembled_status(
                            "running",
                            last_processed_byte_offset=self._byte_offset,
                            last_error="",
                        )

                if self._buffer and (time.time() - self._last_seen_at) >= ASSEMBLER_FLUSH_IDLE_SECONDS:
                    self._flush_buffer()

                time.sleep(POLL_SECONDS)

        except KeyboardInterrupt:
            write_assembled_status("stopped", reason="keyboard_interrupt", last_processed_byte_offset=self._byte_offset)
        except Exception as exc:
            write_assembled_status(
                "error",
                error=f"{type(exc).__name__}: {exc}",
                last_processed_byte_offset=self._byte_offset,
            )
            raise
        finally:
            self._flush_buffer()
            write_assembled_status("stopped", last_processed_byte_offset=self._byte_offset)

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    AssembledTranscriptBuilder().run_forever()
