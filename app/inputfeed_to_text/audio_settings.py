from __future__ import annotations

from dataclasses import dataclass

from .inputfeed_settings import (
    INPUTFEED_CHANNELS,
    INPUTFEED_ENABLE_RNNOISE,
    INPUTFEED_FRAMES_PER_BUFFER,
    INPUTFEED_INPUT_GAIN,
    INPUTFEED_SAMPLE_RATE,
    INPUTFEED_SAMPLE_WIDTH,
    INPUTFEED_SOURCE_BACKEND,
    WINDOWS_MIC_DEVICE_NAME,
)


@dataclass(slots=True)
class InputFeedAudioSettings:
    windows_mic_device_name: str = WINDOWS_MIC_DEVICE_NAME

    input_sample_rate: int = INPUTFEED_SAMPLE_RATE
    input_channels: int = INPUTFEED_CHANNELS
    sample_width: int = INPUTFEED_SAMPLE_WIDTH

    frames_per_buffer: int = INPUTFEED_FRAMES_PER_BUFFER
    input_gain: float = INPUTFEED_INPUT_GAIN

    source_backend: str = INPUTFEED_SOURCE_BACKEND
    enable_rnnoise: bool = INPUTFEED_ENABLE_RNNOISE