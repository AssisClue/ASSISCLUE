from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.context_memory.backends.json.json_memory_store import JsonMemoryStore
from app.context_memory.backends.json.json_profile_store import JsonProfileStore
from app.context_memory.backends.json.json_snapshot_store import JsonSnapshotStore
from app.context_memory.builders.memory_record_builder import MemoryRecordBuilder
from app.context_memory.classify.importance_scorer import ImportanceScorer
from app.context_memory.classify.memory_kind_classifier import MemoryKindClassifier
from app.context_memory.classify.promotion_rules import PromotionRules
from app.context_memory.contracts.context_types import ContextKind, ContextSnapshotMetadata
from app.context_memory.ingest.chat_history_reader import ChatHistoryReader
from app.context_memory.ingest.input_assembler import InputAssembler
from app.context_memory.ingest.live_moment_history_reader import LiveMomentHistoryReader
from app.context_memory.ingest.system_runtime_event_reader import SystemRuntimeEventReader
from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.memory_item import MemoryItem
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot
from app.context_memory.normalize.dedupe_keys import build_dedupe_key
from app.context_memory.orchestration.memory_update_pipeline import MemoryUpdatePipeline
from app.context_memory.runtime.context_memory_runtime_config import ContextMemoryRuntimeConfig
from app.context_memory.runtime.storage_paths import ContextMemoryStoragePaths
from app.context_memory.extract.project_extractor import ProjectExtractor
from app.context_memory.extract.topic_extractor import TopicExtractor


SERVICE_NAME = "context_memory_runtime"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--run-once", action="store_true", help="Run one ingest/persist pass and exit.")
    return parser.parse_args()


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = str(value or "").strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(cleaned)
    return result


class ContextMemoryRuntimeService:
    def __init__(self, config: ContextMemoryRuntimeConfig | None = None) -> None:
        self.config = config or ContextMemoryRuntimeConfig.create_default()
        self.storage_paths = ContextMemoryStoragePaths(runtime_root=self.config.runtime_root)
        self.storage_paths.ensure_directories()
        self.config.status_path.parent.mkdir(parents=True, exist_ok=True)

        self._chat_reader = ChatHistoryReader(self.config.chat_history_path)
        self._live_moment_reader = LiveMomentHistoryReader(self.config.live_moment_history_path)
        self._system_runtime_reader = SystemRuntimeEventReader(self.config.system_runtime_state_path)

        self._memory_store = JsonMemoryStore(self.storage_paths.memory_items_path)
        self._snapshot_store = JsonSnapshotStore(
            live_snapshot_path=self.storage_paths.live_snapshot_path,
            recent_snapshot_path=self.storage_paths.recent_snapshot_path,
        )
        self._profile_store = JsonProfileStore(self.storage_paths.user_profile_snapshot_path)
        self._pipeline = MemoryUpdatePipeline(
            memory_record_builder=MemoryRecordBuilder(),
            memory_kind_classifier=MemoryKindClassifier(),
            importance_scorer=ImportanceScorer(),
            promotion_rules=PromotionRules(),
            project_extractor=ProjectExtractor(),
            topic_extractor=TopicExtractor(),
        )
        self._running = False
        self._status_cache: dict[str, Any] | None = None

    def _load_status(self) -> dict[str, Any]:
        if self._status_cache is not None:
            return self._status_cache
        if not self.config.status_path.exists():
            self._status_cache = {}
            return self._status_cache
        try:
            payload = json.loads(self.config.status_path.read_text(encoding="utf-8"))
            self._status_cache = payload if isinstance(payload, dict) else {}
        except Exception:
            self._status_cache = {}
        return self._status_cache

    def _update_status(self, state: str, **extra: Any) -> None:
        status = self._load_status()
        status["ok"] = state != "error"
        status["state"] = state
        status["service"] = SERVICE_NAME
        status["updated_at"] = time.time()
        status["chat_history_last_processed_byte_offset"] = int(status.get("chat_history_last_processed_byte_offset", 0) or 0)
        status["live_moment_last_processed_byte_offset"] = int(status.get("live_moment_last_processed_byte_offset", 0) or 0)
        status["system_runtime_last_processed_updated_at"] = float(status.get("system_runtime_last_processed_updated_at", 0.0) or 0.0)
        status.update(extra)

    def _flush_status(self) -> None:
        self.config.status_path.write_text(
            json.dumps(self._load_status(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _current_counter(self, existing_items: list[MemoryItem]) -> int:
        highest = 0
        for item in existing_items:
            suffix = str(item.item_id or "").rsplit("_", 1)[-1]
            if suffix.isdigit():
                highest = max(highest, int(suffix))
        return highest

    def _run_pipeline(
        self,
        bundle,
        existing_items: list[MemoryItem],
    ) -> list[MemoryItem]:
        starting_counter = self._current_counter(existing_items)
        setattr(self._pipeline, "_counter", starting_counter)
        return self._pipeline.run(bundle)

    def _merge_items(self, existing_items: list[MemoryItem], new_items: list[MemoryItem]) -> tuple[list[MemoryItem], int]:
        merged = list(existing_items)
        seen = {build_dedupe_key(item.text, source=item.source, kind=item.kind) for item in existing_items}
        added = 0
        for item in new_items:
            key = build_dedupe_key(item.text, source=item.source, kind=item.kind)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
            added += 1
        return merged, added

    def _build_live_snapshot(
        self,
        merged_items: list[MemoryItem],
        live_events: list[str],
        runtime_events: list[str],
    ) -> LiveContextSnapshot:
        latest_focus = ""
        if live_events:
            latest_focus = live_events[-1]
        elif runtime_events:
            latest_focus = runtime_events[-1]
        elif merged_items:
            latest_focus = merged_items[-1].text

        active_topics = _dedupe_preserve_order(
            [tag for item in merged_items[-8:] for tag in item.tags]
        )[:6]
        open_issues = [item.text for item in merged_items if item.kind in {"issue", "coding_issue"}][-3:]
        recent_events = (live_events + runtime_events)[-self.config.live_event_limit :]

        return LiveContextSnapshot(
            current_focus=latest_focus,
            active_topics=active_topics,
            recent_events=recent_events,
            screenshot_notes=[],
            open_issues=open_issues,
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.LIVE,
                ts=time.time(),
                source_count=3,
                item_count=len(merged_items),
            ),
        )

    def _build_recent_snapshot(
        self,
        merged_items: list[MemoryItem],
        live_events: list[str],
        runtime_events: list[str],
    ) -> RecentContextSnapshot:
        sorted_items = sorted(
            merged_items,
            key=lambda item: float(item.ts or 0.0),
            reverse=True,
        )
        summary_lines = [item.text for item in sorted_items[: self.config.recent_summary_limit]]
        recent_topics = _dedupe_preserve_order([tag for item in sorted_items[:12] for tag in item.tags])[:6]
        recent_projects = _dedupe_preserve_order(
            [str(item.project_name or "").strip() for item in sorted_items[:12] if item.project_name]
        )[:6]
        recent_errors = [item.text for item in sorted_items if item.kind in {"issue", "coding_issue"}][:4]
        notable_events = (live_events + runtime_events)[-self.config.recent_summary_limit :]

        return RecentContextSnapshot(
            summary_lines=summary_lines,
            recent_topics=recent_topics,
            recent_projects=recent_projects,
            notable_events=notable_events,
            recent_errors=recent_errors,
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.RECENT,
                ts=time.time(),
                source_count=3,
                item_count=len(merged_items),
            ),
        )

    def _build_profile_snapshot(self, merged_items: list[MemoryItem]) -> UserProfileSnapshot:
        preferences = _dedupe_preserve_order([item.text for item in merged_items if item.kind == "preference"])[:8]
        stable_facts = _dedupe_preserve_order([item.text for item in merged_items if item.kind == "persistent_fact"])[:8]
        active_projects = _dedupe_preserve_order(
            [str(item.project_name or "").strip() for item in merged_items if item.project_name]
        )[:8]

        return UserProfileSnapshot(
            stable_facts=stable_facts,
            preferences=preferences,
            active_projects=active_projects,
            working_style=[],
            metadata=ContextSnapshotMetadata(
                kind=ContextKind.PROFILE,
                ts=time.time(),
                source_count=3,
                item_count=len(preferences) + len(stable_facts),
            ),
        )

    def run_once(self) -> dict[str, Any]:
        status = self._load_status()
        chat_offset = int(status.get("chat_history_last_processed_byte_offset", 0) or 0)
        live_moment_offset = int(status.get("live_moment_last_processed_byte_offset", 0) or 0)
        system_runtime_updated_at = float(status.get("system_runtime_last_processed_updated_at", 0.0) or 0.0)

        chat_messages, chat_offset = self._chat_reader.read_from_offset(chat_offset)
        live_moment_events, live_moment_offset = self._live_moment_reader.read_from_offset(live_moment_offset)
        runtime_events, system_runtime_updated_at = self._system_runtime_reader.read_if_updated(system_runtime_updated_at)

        assembler = InputAssembler()
        assembler.add_chat_messages(chat_messages)
        assembler.add_session_events([*live_moment_events, *runtime_events])
        bundle = assembler.build_bundle()

        existing_items = self._memory_store.load_memory_items()
        new_items = self._run_pipeline(bundle, existing_items)
        merged_items, added_count = self._merge_items(existing_items, new_items)

        if added_count > 0 or len(merged_items) != len(existing_items):
            self._memory_store.save_memory_items(merged_items)

        live_events = [item.text for item in live_moment_events]
        runtime_event_texts = [item.text for item in runtime_events]

        live_snapshot = self._build_live_snapshot(merged_items, live_events, runtime_event_texts)
        recent_snapshot = self._build_recent_snapshot(merged_items, live_events, runtime_event_texts)
        profile_snapshot = self._build_profile_snapshot(merged_items)

        self._snapshot_store.save_live_context_snapshot(live_snapshot)
        self._snapshot_store.save_recent_context_snapshot(recent_snapshot)
        self._profile_store.save_user_profile_snapshot(profile_snapshot)

        result = {
            "chat_messages_seen": len(chat_messages),
            "live_moments_seen": len(live_moment_events),
            "runtime_events_seen": len(runtime_events),
            "new_memory_items": added_count,
            "memory_item_count": len(merged_items),
            "chat_history_last_processed_byte_offset": chat_offset,
            "live_moment_last_processed_byte_offset": live_moment_offset,
            "system_runtime_last_processed_updated_at": system_runtime_updated_at,
            "live_snapshot": asdict(live_snapshot),
            "recent_snapshot": asdict(recent_snapshot),
        }

        self._update_status("running", **result)
        self._flush_status()
        return result

    def run_forever(self) -> None:
        self._running = True
        self._update_status("starting")
        self._flush_status()

        try:
            self._update_status("running")
            self._flush_status()

            while self._running:
                result = self.run_once()
                print(json.dumps(result, ensure_ascii=False), flush=True)
                time.sleep(self.config.poll_seconds)

        except KeyboardInterrupt:
            self._update_status("stopped", reason="keyboard_interrupt")
            self._flush_status()
        except Exception as exc:
            self._update_status("error", error=f"{type(exc).__name__}: {exc}")
            self._flush_status()
            raise
        finally:
            self._update_status("stopped")
            self._flush_status()

    def stop(self) -> None:
        self._running = False


def main() -> None:
    args = _parse_args()
    service = ContextMemoryRuntimeService()

    if args.run_once:
        service._update_status("starting")
        service._flush_status()
        result = service.run_once()
        print(json.dumps(result, ensure_ascii=False), flush=True)
        service._update_status("stopped")
        service._flush_status()
        return

    service.run_forever()


if __name__ == "__main__":
    main()
