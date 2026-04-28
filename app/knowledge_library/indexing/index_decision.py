from __future__ import annotations


class IndexDecision:
    def should_index(self, *, force: bool = True) -> bool:
        return bool(force)