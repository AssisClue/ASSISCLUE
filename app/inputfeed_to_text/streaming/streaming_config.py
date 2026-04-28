from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InputFeedStreamingConfig:
    enabled: bool = False
    step_seconds: float = 1.0
    overlap_seconds: float = 0.25
    max_buffer_seconds: float = 3.0
    commit_stable_passes: int = 2
    recent_segment_count: int = 1
