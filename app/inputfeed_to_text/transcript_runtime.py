from __future__ import annotations

import json
import shutil
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from .inputfeed_settings import (
    ASSEMBLED_TRANSCRIPT_STATUS_JSON,
    INPUTFEED_TO_TEXT_STATUS_JSON,
    LIVE_TRANSCRIPT_ASSEMBLED_JSONL,
    LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON,
    LIVE_TRANSCRIPT_HISTORY_JSONL,
    LIVE_TRANSCRIPT_LATEST_JSON,
    LIVE_TRANSCRIPT_RAW_JSONL,
    LIVE_TRANSCRIPT_RAW_LATEST_JSON,
    RUNTIME_ARCHIVE_DIR,
    RUNTIME_SACRED_DIR,
    RUNTIME_STATUS_DIR,
)


def ensure_runtime_dirs() -> None:
    RUNTIME_SACRED_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for path, default_text in (
        (LIVE_TRANSCRIPT_RAW_JSONL, ""),
        (LIVE_TRANSCRIPT_RAW_LATEST_JSON, "{}\n"),
        (LIVE_TRANSCRIPT_HISTORY_JSONL, ""),
        (LIVE_TRANSCRIPT_LATEST_JSON, "{}\n"),
        (LIVE_TRANSCRIPT_ASSEMBLED_JSONL, ""),
        (LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON, "{}\n"),
    ):
        if not path.exists():
            path.write_text(default_text, encoding="utf-8")


def _clean_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def _build_event_id(prefix: str = "evt") -> str:
    return f"{prefix}_{uuid4().hex}"


def write_inputfeed_status(state: str, **extra: Any) -> None:
    ensure_runtime_dirs()
    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "updated_at": time.time(),
    }
    payload.update(extra)
    INPUTFEED_TO_TEXT_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_assembled_status(state: str, **extra: Any) -> None:
    ensure_runtime_dirs()
    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "service": "assembled_transcript_builder",
        "updated_at": time.time(),
    }
    payload.update(extra)
    ASSEMBLED_TRANSCRIPT_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def append_raw_transcript_line(
    *,
    source: str,
    session_id: str,
    text: str,
    language: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ensure_runtime_dirs()

    record = {
        "event_id": _build_event_id("evt"),
        "ts": time.time(),
        "session_id": session_id,
        "source": source,
        "text": _clean_text(text),
        "language": language,
        "metadata": metadata or {},
    }

    line = json.dumps(record, ensure_ascii=False) + "\n"

    with LIVE_TRANSCRIPT_RAW_JSONL.open("a", encoding="utf-8") as f:
        f.write(line)
    with LIVE_TRANSCRIPT_HISTORY_JSONL.open("a", encoding="utf-8") as f:
        f.write(line)

    latest_text = json.dumps(record, indent=2, ensure_ascii=False)
    LIVE_TRANSCRIPT_RAW_LATEST_JSON.write_text(latest_text, encoding="utf-8")
    LIVE_TRANSCRIPT_LATEST_JSON.write_text(latest_text, encoding="utf-8")

    return record


def append_assembled_transcript_line(
    *,
    session_id: str,
    text: str,
    source_event_ids: list[str],
    start_ts: float,
    end_ts: float,
    part_count: int,
) -> dict[str, Any]:
    ensure_runtime_dirs()

    record = {
        "event_id": _build_event_id("asmb"),
        "ts": time.time(),
        "session_id": session_id,
        "source": "assembled_transcript_builder",
        "text": _clean_text(text),
        "source_event_ids": source_event_ids,
        "part_count": int(part_count),
        "start_ts": float(start_ts or 0.0),
        "end_ts": float(end_ts or 0.0),
    }

    with LIVE_TRANSCRIPT_ASSEMBLED_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON.write_text(
        json.dumps(record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return record


def load_latest_raw_transcript() -> dict[str, Any]:
    ensure_runtime_dirs()
    try:
        return json.loads(LIVE_TRANSCRIPT_RAW_LATEST_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def archive_and_reset_live_transcript(*, session_id: str) -> dict[str, Any]:
    ensure_runtime_dirs()

    if not LIVE_TRANSCRIPT_RAW_JSONL.exists() or LIVE_TRANSCRIPT_RAW_JSONL.stat().st_size == 0:
        for path in (
            LIVE_TRANSCRIPT_RAW_JSONL,
            LIVE_TRANSCRIPT_HISTORY_JSONL,
            LIVE_TRANSCRIPT_ASSEMBLED_JSONL,
        ):
            path.write_text("", encoding="utf-8")
        for path in (
            LIVE_TRANSCRIPT_RAW_LATEST_JSON,
            LIVE_TRANSCRIPT_LATEST_JSON,
            LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON,
        ):
            path.write_text("{}\n", encoding="utf-8")
        return {}

    now = datetime.now()
    archive_dir = RUNTIME_ARCHIVE_DIR / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
    archive_dir.mkdir(parents=True, exist_ok=True)

    raw_archive_path = archive_dir / f"session_{session_id}__raw__{now.strftime('%H-%M-%S')}.jsonl"
    assembled_archive_path = archive_dir / f"session_{session_id}__assembled__{now.strftime('%H-%M-%S')}.jsonl"

    shutil.copy2(LIVE_TRANSCRIPT_RAW_JSONL, raw_archive_path)
    if LIVE_TRANSCRIPT_ASSEMBLED_JSONL.exists() and LIVE_TRANSCRIPT_ASSEMBLED_JSONL.stat().st_size > 0:
        shutil.copy2(LIVE_TRANSCRIPT_ASSEMBLED_JSONL, assembled_archive_path)

    for path in (
        LIVE_TRANSCRIPT_RAW_JSONL,
        LIVE_TRANSCRIPT_HISTORY_JSONL,
        LIVE_TRANSCRIPT_ASSEMBLED_JSONL,
    ):
        path.write_text("", encoding="utf-8")

    for path in (
        LIVE_TRANSCRIPT_RAW_LATEST_JSON,
        LIVE_TRANSCRIPT_LATEST_JSON,
        LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON,
    ):
        path.write_text("{}\n", encoding="utf-8")

    return {
        "archive_dir": str(archive_dir),
        "raw_archive_path": str(raw_archive_path),
        "assembled_archive_path": str(assembled_archive_path),
        "session_id": session_id,
    }