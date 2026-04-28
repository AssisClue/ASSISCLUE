from __future__ import annotations

import json
import time
from typing import Any

from app.live_listeners.shared.listener_paths import (
    CONTEXT_RUNNER_STATUS_JSON,
    RUNTIME_SACRED_DIR,
    ensure_listener_runtime_dirs,
)

CONTEXT_SNAPSHOT_JSON = RUNTIME_SACRED_DIR / "context_snapshot.json"
MEMORY_SNAPSHOT_JSON = RUNTIME_SACRED_DIR / "memory_snapshot.json"
WORLD_STATE_JSON = RUNTIME_SACRED_DIR / "world_state.json"


def write_context_snapshot(payload: dict[str, Any]) -> None:
    ensure_listener_runtime_dirs()
    CONTEXT_SNAPSHOT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_memory_snapshot(payload: dict[str, Any]) -> None:
    ensure_listener_runtime_dirs()
    MEMORY_SNAPSHOT_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_world_state(payload: dict[str, Any]) -> None:
    ensure_listener_runtime_dirs()
    WORLD_STATE_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_context_runner_status(state: str, **extra: Any) -> None:
    ensure_listener_runtime_dirs()

    payload: dict[str, Any] = {
        "ok": state not in {"error"},
        "state": state,
        "listener": "context_runner",
        "updated_at": time.time(),
    }
    payload.update(extra)

    CONTEXT_RUNNER_STATUS_JSON.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )