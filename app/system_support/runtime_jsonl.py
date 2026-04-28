from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time

from app.system_support.text_cleaning import normalize_pipeline_text
from app.system_support.time_utils import format_ts, format_ts_short


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_runtime_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    append_jsonl(path, payload)


def read_new_runtime_jsonl_lines(
    path: str | Path,
    start_offset: int,
    *,
    bom_at_start: bool = False,
    reset_to_start_on_truncate: bool = True,
) -> list[tuple[str, int]]:
    file_path = Path(path)
    if not file_path.exists():
        return []

    file_size = file_path.stat().st_size
    offset = max(0, int(start_offset or 0))
    if offset > file_size:
        offset = 0 if reset_to_start_on_truncate else file_size

    lines: list[tuple[str, int]] = []
    encoding = "utf-8-sig" if (bom_at_start and offset == 0) else "utf-8"
    with file_path.open("r", encoding=encoding) as handle:
        handle.seek(offset)
        while True:
            line_start = handle.tell()
            raw = handle.readline()
            if raw == "":
                break
            if not raw.endswith("\n"):
                handle.seek(line_start)
                break
            lines.append((raw.rstrip("\r\n"), handle.tell()))

    return lines


def read_runtime_jsonl(path: str | Path, limit: int = 50) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

    parsed: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            item["ts_pretty"] = format_ts(item.get("ts"))
            item["ts_short"] = format_ts_short(item.get("ts"))
            parsed.append(item)
        except Exception:
            continue

    return parsed


def build_chat_history_item(
    role: str,
    text: str,
    *,
    persona: str = "",
    model_name: str = "",
    source: str = "",
) -> dict[str, Any]:
    ts = time.time()
    return {
        "role": role,
        "text": normalize_pipeline_text(text),
        "persona": persona,
        "model_name": model_name,
        "source": source,
        "ts": ts,
        "ts_pretty": format_ts(ts),
        "ts_short": format_ts_short(ts),
    }
