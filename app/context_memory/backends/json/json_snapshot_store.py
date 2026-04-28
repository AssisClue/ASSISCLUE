from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot


@dataclass(slots=True)
class JsonSnapshotStore:
    live_snapshot_path: str | Path
    recent_snapshot_path: str | Path

    def __post_init__(self) -> None:
        self.live_snapshot_path = Path(self.live_snapshot_path)
        self.recent_snapshot_path = Path(self.recent_snapshot_path)
        self.live_snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.recent_snapshot_path.parent.mkdir(parents=True, exist_ok=True)

    def save_live_context_snapshot(self, snapshot: LiveContextSnapshot) -> None:
        self.live_snapshot_path.write_text(
            json.dumps(asdict(snapshot), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_live_context_snapshot(self) -> LiveContextSnapshot | None:
        if not self.live_snapshot_path.exists():
            return None

        raw = self.live_snapshot_path.read_text(encoding="utf-8").strip()
        if not raw:
            return None

        data = json.loads(raw)
        if not isinstance(data, dict):
            return None

        metadata = self._parse_metadata(data.get("metadata"), kind=ContextKind.LIVE)
        return LiveContextSnapshot(
            current_focus=str(data.get("current_focus") or ""),
            active_topics=list(data.get("active_topics") or []),
            recent_events=list(data.get("recent_events") or []),
            screenshot_notes=list(data.get("screenshot_notes") or []),
            open_issues=list(data.get("open_issues") or []),
            metadata=metadata,
            extra=dict(data.get("extra") or {}),
        )

    def save_recent_context_snapshot(self, snapshot: RecentContextSnapshot) -> None:
        self.recent_snapshot_path.write_text(
            json.dumps(asdict(snapshot), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_recent_context_snapshot(self) -> RecentContextSnapshot | None:
        if not self.recent_snapshot_path.exists():
            return None

        raw = self.recent_snapshot_path.read_text(encoding="utf-8").strip()
        if not raw:
            return None

        data = json.loads(raw)
        if not isinstance(data, dict):
            return None

        metadata = self._parse_metadata(data.get("metadata"), kind=ContextKind.RECENT)
        return RecentContextSnapshot(
            summary_lines=list(data.get("summary_lines") or []),
            recent_topics=list(data.get("recent_topics") or []),
            recent_projects=list(data.get("recent_projects") or []),
            notable_events=list(data.get("notable_events") or []),
            recent_errors=list(data.get("recent_errors") or []),
            metadata=metadata,
            extra=dict(data.get("extra") or {}),
        )

    def _parse_metadata(
        self,
        payload: object,
        kind: ContextKind,
    ) -> ContextSnapshotMetadata:
        if not isinstance(payload, dict):
            return ContextSnapshotMetadata(kind=kind, ts=0.0)

        return ContextSnapshotMetadata(
            kind=kind,
            ts=float(payload.get("ts") or 0.0),
            source_count=int(payload.get("source_count") or 0),
            item_count=int(payload.get("item_count") or 0),
            tags=list(payload.get("tags") or []),
            extra=dict(payload.get("extra") or {}),
        )