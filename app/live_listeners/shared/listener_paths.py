from __future__ import annotations

from pathlib import Path


SHARED_DIR = Path(__file__).resolve().parent
LIVE_LISTENERS_DIR = SHARED_DIR.parent
APP_DIR = LIVE_LISTENERS_DIR.parent
PROJECT_ROOT = APP_DIR.parent

RUNTIME_DIR = PROJECT_ROOT / "runtime"
RUNTIME_SACRED_DIR = RUNTIME_DIR / "sacred"
RUNTIME_STATUS_DIR = RUNTIME_DIR / "status"
RUNTIME_LIVE_LISTENERS_DIR = RUNTIME_DIR / "state" / "live_listeners"





LIVE_TRANSCRIPT_HISTORY_JSONL = RUNTIME_SACRED_DIR / "live_transcript_history.jsonl"
ASSEMBLED_TRANSCRIPT_JSONL = RUNTIME_DIR / "sacred" / "live_transcript_assembled.jsonl"



LIVE_TRANSCRIPT_LATEST_JSON = RUNTIME_SACRED_DIR / "live_transcript_latest.json"
LIVE_MOMENT_HISTORY_JSONL = RUNTIME_SACRED_DIR / "live_moment_history.jsonl"

PRIMARY_LISTENER_CURSOR_JSON = RUNTIME_LIVE_LISTENERS_DIR / "primary_listener_cursor.json"
ADMINISTRATIVE_LISTENER_CURSOR_JSON = RUNTIME_LIVE_LISTENERS_DIR / "administrative_listener_cursor.json"
CONTEXT_RUNNER_CURSOR_JSON = RUNTIME_LIVE_LISTENERS_DIR / "context_runner_cursor.json"

PRIMARY_LISTENER_STATUS_JSON = RUNTIME_STATUS_DIR / "primary_listener_status.json"
ADMINISTRATIVE_LISTENER_STATUS_JSON = RUNTIME_STATUS_DIR / "administrative_listener_status.json"
CONTEXT_RUNNER_STATUS_JSON = RUNTIME_STATUS_DIR / "context_runner_status.json"


def ensure_listener_runtime_dirs() -> None:
    RUNTIME_SACRED_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_STATUS_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_LIVE_LISTENERS_DIR.mkdir(parents=True, exist_ok=True)
