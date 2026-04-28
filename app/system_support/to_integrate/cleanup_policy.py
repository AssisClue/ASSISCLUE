from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass(slots=True)
class CleanupPolicy:
    runtime_cleanup_days: int = 7
    screenshot_retention_days: int = 3

    def runtime_cutoff(self) -> datetime:
        return datetime.now() - timedelta(days=self.runtime_cleanup_days)

    def screenshot_cutoff(self) -> datetime:
        return datetime.now() - timedelta(days=self.screenshot_retention_days)


def should_delete_file(path: Path, cutoff: datetime) -> bool:
    if not path.exists() or not path.is_file():
        return False

    modified_at = datetime.fromtimestamp(path.stat().st_mtime)
    return modified_at < cutoff