from __future__ import annotations

from .common import BaseUiService


class ActionsService(BaseUiService):
    def scan_all(self) -> dict:
        return self.facade.scan_all()

    def summarize_file(self, item_id: str) -> dict:
        return self.facade.summarize_file(item_id=item_id)

    def index_file(self, item_id: str) -> dict:
        return self.facade.index_file(
            item_id=item_id,
            chunk_size=800,
            chunk_overlap=120,
            write_vectors=False,
            make_summary=True,
        )

    def promote_file(self, item_id: str) -> dict:
        return self.facade.promote_to_context_memory(
            item_id=item_id,
            rebuild_qdrant=False,
        )