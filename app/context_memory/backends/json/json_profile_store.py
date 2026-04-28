from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


@dataclass(slots=True)
class JsonProfileStore:
    storage_path: str | Path

    def __post_init__(self) -> None:
        self.storage_path = Path(self.storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_user_profile_snapshot(self, snapshot: UserProfileSnapshot) -> None:
        self.storage_path.write_text(
            json.dumps(asdict(snapshot), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load_user_profile_snapshot(self) -> UserProfileSnapshot | None:
        if not self.storage_path.exists():
            return None

        raw = self.storage_path.read_text(encoding="utf-8").strip()
        if not raw:
            return None

        data = json.loads(raw)
        if not isinstance(data, dict):
            return None

        metadata = self._parse_metadata(data.get("metadata"), kind=ContextKind.PROFILE)
        return UserProfileSnapshot(
            stable_facts=list(data.get("stable_facts") or []),
            preferences=list(data.get("preferences") or []),
            active_projects=list(data.get("active_projects") or []),
            working_style=list(data.get("working_style") or []),
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