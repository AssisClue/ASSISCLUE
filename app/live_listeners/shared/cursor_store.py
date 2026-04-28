from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .listener_paths import ensure_listener_runtime_dirs


def load_cursor(cursor_path: Path) -> dict[str, Any]:
    ensure_listener_runtime_dirs()

    if not cursor_path.exists():
        return {
            "byte_offset": 0,
            "last_event_id": "",
            "updated_at": 0.0,
        }

    try:
        payload = json.loads(cursor_path.read_text(encoding="utf-8"))
        return {
            "byte_offset": int(payload.get("byte_offset", 0) or 0),
            "last_event_id": str(payload.get("last_event_id", "") or ""),
            "updated_at": float(payload.get("updated_at", 0.0) or 0.0),
        }
    except Exception:
        return {
            "byte_offset": 0,
            "last_event_id": "",
            "updated_at": 0.0,
        }


def save_cursor(
    cursor_path: Path,
    *,
    byte_offset: int,
    last_event_id: str,
) -> dict[str, Any]:
    ensure_listener_runtime_dirs()

    payload = {
        "byte_offset": int(byte_offset),
        "last_event_id": str(last_event_id or ""),
        "updated_at": time.time(),
    }

    cursor_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload


def reset_cursor(cursor_path: Path) -> dict[str, Any]:
    return save_cursor(
        cursor_path,
        byte_offset=0,
        last_event_id="",
    )