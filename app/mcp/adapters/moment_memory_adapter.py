from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _runtime_root() -> Path:
    return _project_root() / "runtime"


def _safe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return raw if isinstance(raw, dict) else {}


@dataclass(slots=True)
class MomentMemoryAdapter:
    """
    MCP-facing adapter for moment_memory snapshots/status.

    Read-only adapter.
    Does not start/stop runners.
    """

    def read_context_snapshot(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "sacred" / "context_snapshot.json")

    def read_memory_snapshot(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "sacred" / "memory_snapshot.json")

    def read_world_state(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "sacred" / "world_state.json")

    def read_context_runner_status(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "status" / "context_runner_status.json")

    def read_context_runner_cursor(self) -> dict[str, Any]:
        return _safe_load_json(_runtime_root() / "state" / "live_listeners" / "context_runner_cursor.json")
