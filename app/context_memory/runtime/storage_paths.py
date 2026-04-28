from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ContextMemoryStoragePaths:
    runtime_root: Path

    @property
    def memory_root(self) -> Path:
        return self.runtime_root / "memory"

    @property
    def memory_state_root(self) -> Path:
        return self.runtime_root / "state" / "memory"

    @property
    def snapshots_root(self) -> Path:
        return self.memory_state_root / "snapshots"

    @property
    def indexes_root(self) -> Path:
        return self.memory_state_root / "indexes"

    @property
    def profile_root(self) -> Path:
        return self.memory_root / "profile"

    @property
    def memory_items_path(self) -> Path:
        return self.memory_root / "memory_items.json"

    @property
    def live_snapshot_path(self) -> Path:
        return self.snapshots_root / "live_context.json"

    @property
    def recent_snapshot_path(self) -> Path:
        return self.snapshots_root / "recent_context.json"

    @property
    def user_profile_snapshot_path(self) -> Path:
        return self.profile_root / "user_profile.json"

    def ensure_directories(self) -> None:
        self.memory_root.mkdir(parents=True, exist_ok=True)
        self.memory_state_root.mkdir(parents=True, exist_ok=True)
        self.snapshots_root.mkdir(parents=True, exist_ok=True)
        self.indexes_root.mkdir(parents=True, exist_ok=True)
        self.profile_root.mkdir(parents=True, exist_ok=True)
