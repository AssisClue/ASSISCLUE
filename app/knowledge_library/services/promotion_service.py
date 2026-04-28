from __future__ import annotations

from app.knowledge_library.orchestration.promote_to_context_pipeline import PromoteToContextPipeline


class PromotionService:
    def __init__(self) -> None:
        self.pipeline = PromoteToContextPipeline()

    def promote_to_context_memory(
        self,
        *,
        item_id: str,
        rebuild_qdrant: bool = False,
    ) -> dict:
        return self.pipeline.promote(
            item_id=item_id,
            rebuild_qdrant=rebuild_qdrant,
        )