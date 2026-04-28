from __future__ import annotations

import time
from dataclasses import dataclass

from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.profile.preference_store import PreferenceStore
from app.context_memory.profile.stable_fact_store import StableFactStore
from app.context_memory.profile.user_profile_memory import UserProfileMemory


@dataclass(slots=True)
class UserProfileBuilder:
    def build(
        self,
        profile_memory: UserProfileMemory,
        preference_store: PreferenceStore,
        stable_fact_store: StableFactStore,
        active_projects: list[str] | None = None,
    ) -> UserProfileSnapshot:
        working_style = profile_memory.get_all()

        return UserProfileSnapshot(
            stable_facts=stable_fact_store.get_all(),
            preferences=preference_store.get_all(),
            active_projects=list(active_projects or []),
            working_style=working_style,
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.PROFILE,
                ts=time.time(),
                source_count=1,
                item_count=len(working_style),
                tags=list(active_projects or []),
            ),
        )