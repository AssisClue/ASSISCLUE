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
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@dataclass(slots=True)
class RuntimeAdapter:
    """
    MCP-facing adapter for runtime/system state.

    Uses system_support as the owner of runtime access.
    """

    def read_system_runtime_state(self) -> dict[str, Any]:
        path = _runtime_root() / "state" / "system_runtime.json"
        return _safe_load_json(path)


    def read_llm_runtime_state(self) -> dict[str, Any]:
        path = _runtime_root() / "state" / "llm_runtime_state.json"
        return _safe_load_json(path)


    def read_recent_chat_history(self, *, limit: int = 20) -> list[dict[str, Any]]:
        clean_limit = max(1, int(limit or 20))
        chat_history_path = _runtime_root() / "output" / "chat_history.jsonl"

        if not chat_history_path.exists() or not chat_history_path.is_file():
            return []

        items: list[dict[str, Any]] = []
        try:
            for line in chat_history_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except Exception:
                    continue
                if isinstance(raw, dict):
                    items.append(raw)
        except Exception:
            return []

        return items[-clean_limit:]



    def read_latest_response(self) -> dict[str, Any]:
        path = _runtime_root() / "output" / "latest_response.json"
        return _safe_load_json(path)

    def read_latest_tts(self) -> dict[str, Any]:
        path = _runtime_root() / "output" / "latest_tts.json"
        return _safe_load_json(path)

    def read_latest_decision(self) -> dict[str, Any]:
        path = _runtime_root() / "state" / "latest_decision.json"
        return _safe_load_json(path)