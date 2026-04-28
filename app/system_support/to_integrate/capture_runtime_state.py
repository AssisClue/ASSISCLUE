from __future__ import annotations

from pathlib import Path
from typing import Any
import time

from app.system_support.runtime_files import write_runtime_json, read_runtime_json
from app.system_support.time_utils import format_ts, format_ts_short


def build_capture_state_payload(
    *,
    loop_name: str,
    status: str,
    source_type: str = "",
    last_run_ts: float | None = None,
    last_success_ts: float | None = None,
    last_output_path: str = "",
    last_error: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "loop_name": loop_name,
        "status": status,
        "source_type": source_type,
        "last_run_ts": last_run_ts,
        "last_success_ts": last_success_ts,
        "last_output_path": last_output_path,
        "last_error": last_error,
        "updated_at": time.time(),
        "last_run_ts_pretty": format_ts(last_run_ts),
        "last_run_ts_short": format_ts_short(last_run_ts),
        "last_success_ts_pretty": format_ts(last_success_ts),
        "last_success_ts_short": format_ts_short(last_success_ts),
    }
    if extra:
        payload["extra"] = extra
    return payload


def _capture_state_path(project_root: str | Path, state_name: str) -> Path:
    root = Path(project_root).resolve()
    return root / "runtime" / "state" / f"{state_name}.json"


def _normalized_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    result = dict(payload)
    result.pop("updated_at", None)
    return result


def write_capture_state(project_root: str | Path, state_name: str, payload: dict[str, Any]) -> None:
    path = _capture_state_path(project_root, state_name)
    write_runtime_json(path, payload)


def write_capture_state_if_changed(
    project_root: str | Path,
    state_name: str,
    payload: dict[str, Any],
) -> bool:
    current = read_capture_state(project_root, state_name)
    if _normalized_payload(current) == _normalized_payload(payload):
        return False

    write_capture_state(project_root, state_name, payload)
    return True


def read_capture_state(project_root: str | Path, state_name: str) -> dict[str, Any] | None:
    path = _capture_state_path(project_root, state_name)
    return read_runtime_json(path)