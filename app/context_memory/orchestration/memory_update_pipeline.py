from __future__ import annotations

from dataclasses import dataclass, field

from app.context_memory.builders.memory_record_builder import MemoryRecordBuilder
from app.context_memory.classify.importance_scorer import ImportanceScorer
from app.context_memory.classify.memory_kind_classifier import MemoryKindClassifier
from app.context_memory.classify.promotion_rules import PromotionRules
from app.context_memory.contracts.input_types import SourceBundleInput
from app.context_memory.extract.project_extractor import ProjectExtractor
from app.context_memory.extract.topic_extractor import TopicExtractor
from app.context_memory.models.memory_item import MemoryItem


@dataclass(slots=True)
class MemoryUpdatePipeline:
    memory_record_builder: MemoryRecordBuilder
    memory_kind_classifier: MemoryKindClassifier
    importance_scorer: ImportanceScorer
    promotion_rules: PromotionRules
    project_extractor: ProjectExtractor
    topic_extractor: TopicExtractor
    id_prefix: str = "mem"
    _counter: int = field(default=0)

    def run(self, bundle: SourceBundleInput) -> list[MemoryItem]:
        built_items: list[MemoryItem] = []

        for message in bundle.chat_messages:
            item = self._build_item(
                text=message.text,
                source=message.source,
                ts=message.ts,
            )
            if item is not None:
                built_items.append(item)

        for event in bundle.session_events:
            item = self._build_item(
                text=event.text,
                source=event.source,
                ts=event.ts,
            )
            if item is not None:
                built_items.append(item)

        for note in bundle.screenshot_notes:
            item = self._build_item(
                text=note.text,
                source=note.source,
                ts=note.ts,
            )
            if item is not None:
                built_items.append(item)

        for file_item in bundle.file_context_items:
            item = self._build_item(
                text=file_item.text,
                source=file_item.source,
                ts=file_item.ts,
            )
            if item is not None:
                built_items.append(item)

        return built_items

    def _build_item(self, text: str, source: str, ts: float | None) -> MemoryItem | None:
        cleaned = text.strip()
        if not cleaned:
            return None

        kind = self.memory_kind_classifier.classify(text=cleaned, source=source)
        importance = self.importance_scorer.score(text=cleaned, kind=kind, source=source)

        if not self.promotion_rules.should_promote(
            text=cleaned,
            kind=kind,
            importance=importance,
        ):
            return None

        self._counter += 1
        item_id = f"{self.id_prefix}_{self._counter:06d}"

        project_name = self.project_extractor.extract(cleaned)
        tags = self.topic_extractor.extract(cleaned)

        return self.memory_record_builder.build(
            item_id=item_id,
            text=cleaned,
            kind=kind,
            source=source,
            importance=importance,
            ts=ts,
            tags=tags,
            project_name=project_name,
        )