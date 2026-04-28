from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.backends.mem0.mem0_adapter import Mem0Adapter
from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


@dataclass(slots=True)
class Mem0ProfileStore:
    mem0_adapter: Mem0Adapter

    def save_user_profile_snapshot(self, snapshot: UserProfileSnapshot) -> None:
        for item in snapshot.stable_facts:
            self.mem0_adapter.add(
                text=item,
                metadata={"kind": "profile_stable_fact", "source": "mem0_profile"},
            )

        for item in snapshot.preferences:
            self.mem0_adapter.add(
                text=item,
                metadata={"kind": "profile_preference", "source": "mem0_profile"},
            )

        for item in snapshot.working_style:
            self.mem0_adapter.add(
                text=item,
                metadata={"kind": "profile_working_style", "source": "mem0_profile"},
            )

    def load_user_profile_snapshot(self) -> UserProfileSnapshot | None:
        raw_items = self.mem0_adapter.dump_all()
        if not raw_items:
            return None

        stable_facts: list[str] = []
        preferences: list[str] = []
        working_style: list[str] = []

        for raw in raw_items:
            text = str(raw.get("text") or "").strip()
            metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
            kind = str(metadata.get("kind") or "")

            if not text:
                continue

            if kind == "profile_stable_fact":
                stable_facts.append(text)
            elif kind == "profile_preference":
                preferences.append(text)
            elif kind == "profile_working_style":
                working_style.append(text)

        return UserProfileSnapshot(
            stable_facts=stable_facts,
            preferences=preferences,
            active_projects=[],
            working_style=working_style,
            metadata=ContextSnapshotMetadata(kind=ContextKind.PROFILE, ts=0.0),
        )