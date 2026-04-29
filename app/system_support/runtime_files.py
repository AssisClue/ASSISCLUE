from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time
import os
import tempfile

from app.system_support.text_cleaning import normalize_pipeline_text


def write_runtime_json(path: str | Path, payload: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{file_path.name}.",
        suffix=".tmp",
        dir=str(file_path.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
        os.replace(tmp_name, file_path)
    finally:
        try:
            if Path(tmp_name).exists():
                Path(tmp_name).unlink()
        except Exception:
            pass


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
