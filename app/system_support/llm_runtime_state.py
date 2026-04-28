from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import time

from app.generation import get_llm_debug_status


@dataclass(slots=True)
class LLMRuntimeState:
    provider: str = "ollama"
    model_name: str = ""
    status: str = "unknown"
    success: bool = False
    error: str = ""
    checked_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


def build_llm_runtime_state(model_name: str) -> LLMRuntimeState:
    debug = get_llm_debug_status(model_name)

    return LLMRuntimeState(
        provider=debug.provider,
        model_name=debug.model_name,
        status=debug.status,
        success=debug.success,
        error=debug.error,
        checked_at=time.time(),
        metadata=debug.metadata,
    )


def save_llm_runtime_state(path: str | Path, state: LLMRuntimeState) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps(asdict(state), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def load_llm_runtime_state(path: str | Path) -> LLMRuntimeState | None:
    file_path = Path(path)
    if not file_path.exists():
        return None

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return LLMRuntimeState(**data)
    except Exception:
        return None