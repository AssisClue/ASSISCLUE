from __future__ import annotations

from typing import Any

from .context_runner_config import CONTEXT_WINDOW_MAX_MOMENTS


class ContextWindowBuilder:
    def __init__(self, *, max_moments: int = CONTEXT_WINDOW_MAX_MOMENTS) -> None:
        self.max_moments = max_moments

    def build_window(
        self,
        current_window: list[dict[str, Any]],
        new_moment: dict[str, Any],
    ) -> list[dict[str, Any]]:
        window = [*current_window, new_moment]
        if len(window) > self.max_moments:
            window = window[-self.max_moments :]
        return window