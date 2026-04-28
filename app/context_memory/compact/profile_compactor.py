from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.normalize.memory_text_normalizer import normalize_memory_text


@dataclass(slots=True)
class ProfileCompactor:
    def compact(self, snapshot: UserProfileSnapshot) -> UserProfileSnapshot:
        snapshot.stable_facts = self._dedupe(snapshot.stable_facts)
        snapshot.preferences = self._dedupe(snapshot.preferences)
        snapshot.active_projects = self._dedupe(snapshot.active_projects)
        snapshot.working_style = self._dedupe(snapshot.working_style)
        return snapshot

    def _dedupe(self, items: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for item in items:
            cleaned = item.strip()
            if not cleaned:
                continue

            key = normalize_memory_text(cleaned)
            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result