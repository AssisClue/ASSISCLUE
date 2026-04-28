from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(slots=True)
class ContextMemoryRuntimeConfig:
    project_root: Path
    poll_seconds: float
    chat_history_limit: int
    recent_summary_limit: int
    live_event_limit: int

    @classmethod
    def create_default(cls, project_root: Path | None = None) -> "ContextMemoryRuntimeConfig":
        resolved_root = project_root or Path(__file__).resolve().parents[3]
        return cls(
            project_root=resolved_root,
            poll_seconds=float(os.getenv("CONTEXT_MEMORY_RUNTIME_POLL_SECONDS", "1.50")),
            chat_history_limit=int(os.getenv("CONTEXT_MEMORY_CHAT_HISTORY_LIMIT", "200")),
            recent_summary_limit=int(os.getenv("CONTEXT_MEMORY_RECENT_SUMMARY_LIMIT", "8")),
            live_event_limit=int(os.getenv("CONTEXT_MEMORY_LIVE_EVENT_LIMIT", "6")),
        )

    @property
    def runtime_root(self) -> Path:
        return self.project_root / "runtime"

    @property
    def chat_history_path(self) -> Path:
        return self.runtime_root / "output" / "chat_history.jsonl"

    @property
    def live_moment_history_path(self) -> Path:
        return self.runtime_root / "sacred" / "live_moment_history.jsonl"

    @property
    def system_runtime_state_path(self) -> Path:
        return self.runtime_root / "state" / "system_runtime.json"

    @property
    def status_path(self) -> Path:
        return self.runtime_root / "status" / "memory" / "context_memory_runtime_status.json"
