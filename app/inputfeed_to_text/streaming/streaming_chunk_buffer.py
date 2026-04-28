from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PCMBufferConfig:
    sample_rate: int
    channels: int
    sample_width: int
    max_buffer_seconds: float


class PCMChunkBuffer:
    def __init__(self, config: PCMBufferConfig) -> None:
        self.config = config
        self._pcm = b""

    @property
    def bytes_per_second(self) -> int:
        return (
            self.config.sample_rate
            * self.config.channels
            * self.config.sample_width
        )

    @property
    def max_bytes(self) -> int:
        return int(self.bytes_per_second * self.config.max_buffer_seconds)

    def append(self, pcm_bytes: bytes) -> None:
        if not pcm_bytes:
            return
        self._pcm += pcm_bytes
        if len(self._pcm) > self.max_bytes:
            self._pcm = self._pcm[-self.max_bytes :]

    def get_pcm(self) -> bytes:
        return self._pcm

    def clear(self) -> None:
        self._pcm = b""