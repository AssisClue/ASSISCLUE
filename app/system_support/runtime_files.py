from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time

from app.system_support.text_cleaning import normalize_pipeline_text


def write_runtime_json(path: str | Path, payload: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_runtime_json(path: str | Path) -> dict[str, Any] | None:
    file_path = Path(path)

    if not file_path.exists():
        return None

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_runtime_message_payload(text: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "text": normalize_pipeline_text(text),
        "ts": time.time(),
    }
    if extra:
        payload.update(extra)
    return payload
