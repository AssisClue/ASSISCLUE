from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.profile.preference_store import PreferenceStore
from app.context_memory.profile.stable_fact_store import StableFactStore
from app.context_memory.profile.user_profile_memory import UserProfileMemory


@dataclass(slots=True)
class ProfileMergeRules:
    def merge_to_snapshot(
        self,
        user_profile_memory: UserProfileMemory,
        preference_store: PreferenceStore,
        stable_fact_store: StableFactStore,
        active_projects: list[str] | None = None,
        working_style: list[str] | None = None,
    ) -> UserProfileSnapshot:
        return UserProfileSnapshot(
            stable_facts=stable_fact_store.get_all(),
            preferences=preference_store.get_all(),
            active_projects=[item.strip() for item in (active_projects or []) if item.strip()],
            working_style=[
                item.strip() for item in (working_style or user_profile_memory.get_all()) if item.strip()
            ],
        )