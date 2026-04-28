from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


def _clean_space_id(space_id: str) -> str:
    cleaned = "".join(ch for ch in str(space_id or "").strip().lower() if ch.isalnum() or ch in {"_", "-"})
    return cleaned or "default"


@dataclass(slots=True)
class UserSpacesStoragePaths:
    runtime_root: Path

    @property
    def user_spaces_dir(self) -> Path:
        return self.runtime_root / "memory" / "user_spaces"

    def ensure_directories(self) -> None:
        self.user_spaces_dir.mkdir(parents=True, exist_ok=True)

    def space_path(self, space_id: str) -> Path:
        return self.user_spaces_dir / f"{_clean_space_id(space_id)}.json"

