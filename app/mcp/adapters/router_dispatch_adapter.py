from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any



_ALLOWED_QUEUES = ("router_input", "action", "response")
_QUEUE_FILENAMES = {
    "router_input": "router_input_queue.jsonl",
    "action": "action_queue.jsonl",
    "response": "response_queue.jsonl",
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _runtime_root() -> Path:
    return _project_root() / "runtime"


def _router_dispatch_root() -> Path:
    return _runtime_root() / "queues" / "router_dispatch"


def _safe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}

    return payload if isinstance(payload, dict) else {}


def _tail_jsonl(path: Path, *, limit: int) -> dict[str, Any]:

    clean_limit = min(200, max(1, int(limit or 50)))

    if not path.exists() or not path.is_file():
        return {
            "items": [],
            "count": 0,
            "limit": clean_limit,
            "invalid_line_count": 0,
            "dropped_incomplete_line": False,
        }

    try:
        raw_text = path.read_text(encoding="utf-8-sig")
    except Exception:
        return {
            "items": [],
            "count": 0,
            "limit": clean_limit,
            "invalid_line_count": 0,
            "dropped_incomplete_line": False,
        }

    dropped_incomplete_line = False
    lines = raw_text.splitlines()
    if raw_text and not raw_text.endswith(("\n", "\r")) and lines:
        lines = lines[:-1]
        dropped_incomplete_line = True

    selected_lines = lines[-clean_limit:]
    items: list[Any] = []
    invalid_line_count = 0

    for line in selected_lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            items.append(json.loads(stripped))
        except Exception:
            invalid_line_count += 1

    return {
        "items": items,
        "count": len(items),
        "limit": clean_limit,
        "invalid_line_count": invalid_line_count,
        "dropped_incomplete_line": dropped_incomplete_line,
    }


@dataclass(slots=True)
class RouterDispatchAdapter:
    """
    MCP-facing adapter for read-only router_dispatch inspection.
    """

    def read_router_dispatch_status(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "status" / "router_dispatch" / "router_status.json")

    def tail_router_dispatch_queue(self, *, queue: str, limit: int = 50) -> dict[str, Any]:
        clean_queue = str(queue or "").strip().lower()
        if clean_queue not in _ALLOWED_QUEUES:
            return {
                "queue": clean_queue,
                "items": [],
                "count": 0,
                "limit": min(200, max(1, int(limit or 50))),
                "invalid_line_count": 0,
                "dropped_incomplete_line": False,
                "error": "invalid_queue",
                "allowed_queues": list(_ALLOWED_QUEUES),
            }

        payload = _tail_jsonl(
            _router_dispatch_root() / _QUEUE_FILENAMES[clean_queue],
            limit=limit,
        )
    
        payload["queue"] = clean_queue
        payload["path"] = str(_router_dispatch_root() / _QUEUE_FILENAMES[clean_queue]) 

        return payload
