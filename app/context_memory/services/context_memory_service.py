from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.context_memory.backends.json.json_memory_store import JsonMemoryStore
from app.context_memory.backends.json.json_profile_store import JsonProfileStore
from app.context_memory.backends.json.json_snapshot_store import JsonSnapshotStore
from app.context_memory.contracts.retrieval_types import (
    RetrievalFilters,
    RetrievalQuery,
    RetrievalResult,
)
from app.context_memory.contracts.task_types import TaskContextHint, TaskType
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.runtime.storage_paths import ContextMemoryStoragePaths
from app.context_memory.user_spaces.user_spaces_service import UserSpacesService
from app.personas.services.persona_service import PersonaService


def _tokenize_words(text: str) -> set[str]:
    cleaned = str(text or "").lower()
    for ch in ",.?;:!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    return {w for w in cleaned.split() if w}


@dataclass(slots=True)
class MemoryQueryAnswer:
    ok: bool
    query: str
    memory_hits: int
    matches: list[str] = field(default_factory=list)
    summary_lines: list[str] = field(default_factory=list)
    fallback_reason: str = ""


@dataclass(slots=True)
class ContextMemoryService:
    memory_items: list[MemoryItem] = field(default_factory=list)
    live_snapshot: LiveContextSnapshot = field(default_factory=LiveContextSnapshot)
    recent_snapshot: RecentContextSnapshot = field(default_factory=RecentContextSnapshot)
    profile_snapshot: UserProfileSnapshot = field(default_factory=UserProfileSnapshot)
    user_spaces_service: UserSpacesService | None = None
    persona_service: PersonaService | None = None

    @classmethod
    def create_default(cls) -> "ContextMemoryService":
        project_root = Path(__file__).resolve().parents[3]
        storage_paths = ContextMemoryStoragePaths(runtime_root=project_root / "runtime")
        storage_paths.ensure_directories()

        memory_store = JsonMemoryStore(storage_path=storage_paths.memory_items_path)
        profile_store = JsonProfileStore(storage_path=storage_paths.user_profile_snapshot_path)
        snapshot_store = JsonSnapshotStore(
            live_snapshot_path=storage_paths.live_snapshot_path,
            recent_snapshot_path=storage_paths.recent_snapshot_path,
        )

        return cls(
            memory_items=memory_store.load_memory_items(),
            live_snapshot=snapshot_store.load_live_context_snapshot() or LiveContextSnapshot(),
            recent_snapshot=snapshot_store.load_recent_context_snapshot() or RecentContextSnapshot(),
            profile_snapshot=profile_store.load_user_profile_snapshot() or UserProfileSnapshot(),
            user_spaces_service=UserSpacesService.create_default(),
            persona_service=PersonaService(project_root / "app" / "personas" / "profiles"),
        )

    def get_live_context(self) -> LiveContextSnapshot:
        return self.live_snapshot

    def get_recent_context(self) -> RecentContextSnapshot:
        return self.recent_snapshot

    def get_user_profile_context(self) -> UserProfileSnapshot:
        return self.profile_snapshot

    def get_task_context(
        self,
        task_type: TaskType,
        query: str = "",
        hint: TaskContextHint | None = None,
    ) -> TaskContextPacket:
        resolved_hint = hint or TaskContextHint()
        matched_items = self._basic_search(query=query, filters=None)

        return TaskContextPacket(
            task_type=task_type,
            query=query,
            summary_lines=self._build_summary_lines(task_type=task_type, query=query),
            memory_items=matched_items,
            recent_items=self.recent_snapshot.summary_lines[:8],
            profile_items=self.profile_snapshot.preferences[:8] + self.profile_snapshot.stable_facts[:8],
            screenshot_notes=self.live_snapshot.screenshot_notes[:8],
            project_name=resolved_hint.project_name,
            metadata={
                "memory_hits": len(matched_items),
                "preferred_sources": resolved_hint.preferred_sources,
                "tags": resolved_hint.tags,
            },
        )

    def search_memory(
        self,
        query: str,
        filters: RetrievalFilters | None = None,
        hint: TaskContextHint | None = None,
    ) -> list[RetrievalResult]:
        matched_items = self._basic_search(query=query, filters=filters, hint=hint)
        results: list[RetrievalResult] = []
        for item in matched_items:
            results.append(
                RetrievalResult(
                    item_id=item.item_id,
                    text=item.text,
                    score=self._score_item(query=query, item=item),
                    kind=item.kind,
                    source=item.source,
                    ts=item.ts,
                    metadata=item.metadata,
                )
            )
        return results

    def answer_memory_query(
        self,
        query: str,
        *,
        limit: int = 5,
        hint: TaskContextHint | None = None,
    ) -> MemoryQueryAnswer:
        cleaned_query = str(query or "").strip()
        if not cleaned_query:
            return MemoryQueryAnswer(
                ok=True,
                query=cleaned_query,
                memory_hits=0,
                fallback_reason="empty_query",
            )

        task_packet = self.get_task_context(
            task_type=TaskType.MEMORY_SEARCH,
            query=cleaned_query,
            hint=hint,
        )
        search_results = self.search_memory(
            cleaned_query,
            filters=RetrievalFilters(limit=limit),
            hint=hint,
        )

        matches = [result.text.strip() for result in search_results if str(result.text).strip()]
        summary_lines = [line.strip() for line in task_packet.summary_lines if str(line).strip()]

        return MemoryQueryAnswer(
            ok=True,
            query=cleaned_query,
            memory_hits=len(matches),
            matches=matches[:limit],
            summary_lines=summary_lines[:limit],
            fallback_reason="" if matches else "no_match",
        )

    def _basic_search(
        self,
        query: str,
        filters: RetrievalFilters | None,
        hint: TaskContextHint | None = None,
    ) -> list[MemoryItem]:
        cleaned_query = query.strip().lower()
        query_words = {word for word in cleaned_query.split() if word}

        candidates = self._build_candidates(query=query, filters=filters, hint=hint)
        if filters is not None:
            candidates = self._apply_filters(candidates, filters)

        if not query_words:
            sorted_items = sorted(candidates, key=lambda item: item.importance, reverse=True)
            return sorted_items[: (filters.limit if filters else 8)]

        scored: list[tuple[float, MemoryItem]] = []
        for item in candidates:
            score = self._score_item(query=query, item=item)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        limit = filters.limit if filters else 8
        return [item for _, item in scored[:limit]]

    def _build_candidates(
        self,
        *,
        query: str,
        filters: RetrievalFilters | None,
        hint: TaskContextHint | None,
    ) -> list[MemoryItem]:
        candidates = list(self.memory_items)
        effective_sources: list[str] = []
        if filters is not None and isinstance(filters.sources, list) and filters.sources:
            effective_sources = [str(value).strip() for value in filters.sources if str(value).strip()]
        elif hint is not None and isinstance(hint.preferred_sources, list) and hint.preferred_sources:
            effective_sources = [str(value).strip() for value in hint.preferred_sources if str(value).strip()]

        user_spaces_sources = [src for src in effective_sources if src.startswith("user_spaces.") or src == "user_spaces.*"]
        if user_spaces_sources and self.user_spaces_service is not None:
            space_ids: list[str] | None = None
            if "user_spaces.*" not in user_spaces_sources:
                space_ids = []
                for src in user_spaces_sources:
                    tail = src.split(".", 1)[1] if "." in src else ""
                    if tail and tail != "*":
                        space_ids.append(tail)
            candidates.extend(
                self.user_spaces_service.search(
                    query=query,
                    space_ids=space_ids,
                    limit=(filters.limit if filters else 8),
                )
            )

        if any(src == "personas" or src.startswith("personas.") for src in effective_sources):
            candidates.extend(self._search_personas(query=query, limit=(filters.limit if filters else 8)))

        return candidates

    def _search_personas(self, *, query: str, limit: int) -> list[MemoryItem]:
        if self.persona_service is None:
            return []

        scored: list[tuple[float, MemoryItem]] = []
        for persona_id in self.persona_service.list_profiles():
            profile = self.persona_service.get_profile(persona_id)
            if profile is None:
                continue

            summary_bits = [
                f"Persona {profile.persona_id}.",
                f"Display name {profile.display_name}.",
            ]
            if profile.style_prompt:
                summary_bits.append(f"Style {profile.style_prompt}")
            if profile.attitude:
                summary_bits.append(f"Attitude {profile.attitude}.")
            if profile.rules:
                summary_bits.append(f"Rules {' '.join(profile.rules)}")

            parts = [
                profile.persona_id,
                profile.display_name,
                "profile persona assistant",
                " ".join(summary_bits),
            ]
            text = " ".join(part.strip() for part in parts if str(part).strip())
            if not text:
                continue

            item = MemoryItem(
                item_id=f"persona_{profile.persona_id}",
                text=text,
                kind="persona_profile",
                source="personas",
                importance=0.95,
                tags=[profile.persona_id.lower()],
                metadata={
                    "persona_id": profile.persona_id,
                    "display_name": profile.display_name,
                },
            )
            score = self._score_item(query=query, item=item)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[: max(1, int(limit or 8))]]

    def _apply_filters(
        self,
        items: list[MemoryItem],
        filters: RetrievalFilters,
    ) -> list[MemoryItem]:
        filtered = items

        if filters.kinds:
            allowed = {value.lower() for value in filters.kinds}
            filtered = [item for item in filtered if item.kind.lower() in allowed]

        if filters.sources:
            allowed_raw = {str(value).strip().lower() for value in filters.sources if str(value).strip()}
            allowed_exact = {value for value in allowed_raw if not value.endswith(".*")}
            allowed_prefixes = [value[:-1] for value in allowed_raw if value.endswith(".*")]

            filtered = [
                item for item in filtered
                if item.source.lower() in allowed_exact
                or any(item.source.lower().startswith(prefix) for prefix in allowed_prefixes)
            ]

        if filters.project_names:
            allowed = {value.lower() for value in filters.project_names}
            filtered = [
                item for item in filtered
                if item.project_name and item.project_name.lower() in allowed
            ]

        if filters.tags:
            wanted = {value.lower() for value in filters.tags}
            filtered = [
                item for item in filtered
                if wanted.intersection({tag.lower() for tag in item.tags})
            ]

        if filters.min_ts is not None:
            filtered = [
                item for item in filtered
                if item.ts is not None and item.ts >= filters.min_ts
            ]

        if filters.max_ts is not None:
            filtered = [
                item for item in filtered
                if item.ts is not None and item.ts <= filters.max_ts
            ]

        return filtered

    def _score_item(self, query: str, item: MemoryItem) -> float:
        query_words = _tokenize_words(query)
        if not query_words:
            return item.importance

        text_words = _tokenize_words(item.text)
        overlap = len(query_words.intersection(text_words))
        if overlap <= 0:
            return 0.0

        return float(overlap) + float(item.importance)

    def _build_summary_lines(self, task_type: TaskType, query: str) -> list[str]:
        lines: list[str] = []

        if self.live_snapshot.current_focus:
            lines.append(f"Current focus: {self.live_snapshot.current_focus}")

        lines.extend(self.recent_snapshot.summary_lines[:4])

        if query.strip():
            lines.append(f"Query: {query.strip()}")

        lines.append(f"Task type: {task_type.value}")
        return lines[:8]
