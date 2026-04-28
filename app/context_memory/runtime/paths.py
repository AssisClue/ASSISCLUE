from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ContextMemoryPaths:
    app_root: Path

    @property
    def context_memory_root(self) -> Path:
        return self.app_root / "app" / "context_memory"

    @property
    def runtime_root(self) -> Path:
        return self.app_root / "runtime"

    @property
    def output_root(self) -> Path:
        return self.runtime_root / "output"

    @property
    def state_root(self) -> Path:
        return self.runtime_root / "state"

    @property
    def memory_root(self) -> Path:
        return self.runtime_root / "memory"