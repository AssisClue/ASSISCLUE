from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(slots=True)
class RecencyScorer:
    def score(self, ts: float | None) -> float:
        if ts is None:
            return 0.0

        now = time.time()
        age_seconds = max(now - ts, 0.0)

        if age_seconds <= 60 * 10:
            return 1.0
        if age_seconds <= 60 * 60:
            return 0.85
        if age_seconds <= 60 * 60 * 6:
            return 0.65
        if age_seconds <= 60 * 60 * 24:
            return 0.45
        if age_seconds <= 60 * 60 * 24 * 7:
            return 0.25
        return 0.10