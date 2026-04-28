from __future__ import annotations

from pathlib import Path
from typing import Any
import time

from app.system_support.runtime_files import read_runtime_json, write_runtime_json


HELP_EXPLAIN_CAPTURE_DEFAULT = True


def system_runtime_state_path(project_root: str | Path) -> Path:
    root = Path(project_root).resolve()
    return root / "runtime" / "state" / "system_runtime.json"


def play_loop_state_path(project_root: str | Path) -> Path:
    root = Path(project_root).resolve()
    return root / "runtime" / "state" / "assistant_play_loop.json"


def read_system_runtime_state(project_root: str | Path) -> dict[str, Any]:
    path = system_runtime_state_path(project_root)
    return read_runtime_json(path) or {}


def read_play_loop_state(project_root: str | Path) -> dict[str, Any]:
    path = play_loop_state_path(project_root)
    return read_runtime_json(path) or {}


def _normalized_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result.pop("updated_at", None)
    return result


def write_system_runtime_state(project_root: str | Path, payload: dict[str, Any]) -> None:
    path = system_runtime_state_path(project_root)
    previous = read_runtime_json(path) or {}

    merged: dict[str, Any] = dict(previous)
    merged.update(dict(payload))
    merged["updated_at"] = time.time()
    merged["started_at"] = merged.get("started_at") or previous.get("started_at") or time.time()

    write_runtime_json(path, merged)


def build_system_runtime_payload(
    *,
    status: str,
    active_mode: str,
    active_persona: str,
    ui_running: bool,
    assistant_loop_running: bool,
    stt_loop_running: bool,
    screenshot_loop_running: bool,
    ui_pid: int | None = None,
    assistant_loop_pid: int | None = None,
    stt_loop_pid: int | None = None,
    screenshot_loop_pid: int | None = None,
    conversation_state: str = "idle",
    last_error: str = "",
) -> dict[str, Any]:
    return {
        "status": status,
        "active_mode": active_mode,
        "active_persona": active_persona,
        "ui_running": ui_running,
        "assistant_loop_running": assistant_loop_running,
        "stt_loop_running": stt_loop_running,
        "screenshot_loop_running": screenshot_loop_running,
        "ui_pid": ui_pid,
        "assistant_loop_pid": assistant_loop_pid,
        "stt_loop_pid": stt_loop_pid,
        "screenshot_loop_pid": screenshot_loop_pid,
        "conversation_state": conversation_state,
        "last_error": last_error,
        "started_at": time.time(),
        "help_explain_capture_enabled": HELP_EXPLAIN_CAPTURE_DEFAULT,
    }


def write_play_loop_state(project_root: str | Path, payload: dict[str, Any]) -> None:
    path = play_loop_state_path(project_root)
    previous = read_runtime_json(path) or {}

    payload = dict(payload)
    payload["updated_at"] = time.time()
    payload["started_at"] = payload.get("started_at") or previous.get("started_at") or time.time()

    write_runtime_json(path, payload)


def write_play_loop_state_if_changed(project_root: str | Path, payload: dict[str, Any]) -> bool:
    current = read_play_loop_state(project_root)
    if _normalized_payload(current) == _normalized_payload(payload):
        return False

    write_play_loop_state(project_root, payload)
    return True


def is_edit_mode_active(project_root: str | Path) -> bool:
    payload = read_system_runtime_state(project_root) or {}
    return bool(payload.get("edit_mode_active", False))


def set_edit_mode(project_root: str | Path, *, active: bool) -> None:
    write_system_runtime_state(
        project_root,
        {
            "edit_mode_active": bool(active),
            "edit_mode_updated_at": time.time(),
        },
    )


def consume_edit_mode_if_active(project_root: str | Path) -> bool:
    if not is_edit_mode_active(project_root):
        return False
    set_edit_mode(project_root, active=False)
    return True


def is_help_explain_capture_enabled(project_root: str | Path) -> bool:
    payload = read_system_runtime_state(project_root) or {}
    return bool(payload.get("help_explain_capture_enabled", HELP_EXPLAIN_CAPTURE_DEFAULT))


def set_help_explain_capture(project_root: str | Path, *, enabled: bool) -> None:
    write_system_runtime_state(
        project_root,
        {
            "help_explain_capture_enabled": bool(enabled),
            "help_explain_capture_updated_at": time.time(),
        },
    )


def ensure_help_explain_capture_default(
    project_root: str | Path,
    *,
    enabled: bool = HELP_EXPLAIN_CAPTURE_DEFAULT,
    force: bool = True,
) -> None:
    payload = read_system_runtime_state(project_root) or {}

    if force or "help_explain_capture_enabled" not in payload:
        set_help_explain_capture(project_root, enabled=enabled)