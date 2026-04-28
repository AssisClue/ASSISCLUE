from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class StreamingChunkResult:
    pcm_bytes: bytes
    sample_rate: int
    channels: int
    sample_width: int
    metadata: dict[str, Any]


@dataclass(slots=True)
class StreamingEmit:
    text: str
    rms: int
    speech_duration_ms: int
    speech_segments: int
    gate_backend: str
    metadata: dict[str, Any]