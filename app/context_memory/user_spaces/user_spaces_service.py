from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.context_memory.models.memory_item import MemoryItem

from .json_user_space_store import JsonUserSpaceStore
from .models import UserSpaceItem
from .storage_paths import UserSpacesStoragePaths


def _tokenize(text: str) -> set[str]:
    cleaned = str(text or "").lower()
    for ch in ",.?;:!\"'()[]{}":
        cleaned = cleaned.replace(ch, " ")
    return {w for w in cleaned.split() if w}


def _score_overlap(query: str, text: str) -> float:
    q_words = _tokenize(query)
    t_words = _tokenize(text)
    if not q_words or not t_words:
        return 0.0
    return float(len(q_words.intersection(t_words)))


@dataclass(slots=True)
class UserSpacesService:
    store: JsonUserSpaceStore

    @classmethod
    def create_default(cls) -> "UserSpacesService":
        project_root = Path(__file__).resolve().parents[3]
        storage_paths = UserSpacesStoragePaths(runtime_root=project_root / "runtime")
        return cls(store=JsonUserSpaceStore(storage_paths))

    def list_spaces(self) -> list[str]:
        return self.store.list_spaces()

    def add_note(
        self,
        *,
        text: str,
        title: str = "",
    ) -> UserSpaceItem:
        clean_text = str(text or "").strip()
        if not clean_text:
            raise ValueError("Note text is empty.")

        return self.store.upsert_item(
            space_id="notes",
            text=clean_text,
            title=str(title or "").strip(),
            metadata={"source": "command_core"},
        )

    def search(
        self,
        *,
        query: str,
        space_ids: list[str] | None = None,
        limit: int = 8,
    ) -> list[MemoryItem]:
        cleaned_query = str(query or "").strip()
        if not cleaned_query:
            return []

        spaces = space_ids or self.list_spaces()
        scored: list[tuple[float, MemoryItem]] = []
        for space_id in spaces:
            for item in self.store.load_space(space_id):
                score = _score_overlap(cleaned_query, item.text)
                if score <= 0:
                    continue
                scored.append(
                    (
                        score,
                        MemoryItem(
                            item_id=item.item_id,
                            text=item.text,
                            kind="user_space_item",
                            source=f"user_spaces.{item.space_id}",
                            importance=0.9,
                            ts=item.ts,
                            tags=list(item.tags),
                            metadata=dict(item.metadata),
                        ),
                    )
                )

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [mem for _, mem in scored[: max(1, int(limit or 8))]]
