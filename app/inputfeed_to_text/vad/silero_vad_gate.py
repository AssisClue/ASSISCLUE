from __future__ import annotations

import audioop
from dataclasses import dataclass

import torch


@dataclass(slots=True)
class SileroVadDecision:
    should_transcribe: bool
    reason: str
    rms: int
    speech_duration_ms: int
    speech_segments: int
    gate_backend: str


class SileroVadGate:
    def __init__(
        self,
        *,
        sample_rate: int,
        sample_width: int,
        min_rms: int,
        min_speech_duration_ms: int,
        min_speech_segments: int,
        threshold: float,
        min_silence_duration_ms: int,
        speech_pad_ms: int,
    ) -> None:
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.min_rms = min_rms
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_speech_segments = min_speech_segments
        self.threshold = threshold
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms

        self._model = None
        self._get_speech_timestamps = None
        self._load_error = ""

        try:
            from silero_vad import get_speech_timestamps, load_silero_vad  # type: ignore

            self._model = load_silero_vad()
            self._get_speech_timestamps = get_speech_timestamps
        except Exception as exc:
            self._load_error = f"{type(exc).__name__}: {exc}"

    @property
    def available(self) -> bool:
        return self._model is not None and self._get_speech_timestamps is not None

    @property
    def load_error(self) -> str:
        return self._load_error

    def _pcm_to_tensor(self, pcm_bytes: bytes) -> torch.Tensor:
        audio = torch.frombuffer(bytearray(pcm_bytes), dtype=torch.int16).to(torch.float32)
        audio = audio / 32768.0
        return audio

    def decide(self, pcm_bytes: bytes) -> SileroVadDecision:
        try:
            rms = int(audioop.rms(pcm_bytes, self.sample_width))
        except Exception:
            rms = 0

        if not pcm_bytes:
            return SileroVadDecision(
                should_transcribe=False,
                reason="empty_chunk",
                rms=rms,
                speech_duration_ms=0,
                speech_segments=0,
                gate_backend="silero_vad",
            )

        if rms < self.min_rms:
            return SileroVadDecision(
                should_transcribe=False,
                reason="silence_gate_rms",
                rms=rms,
                speech_duration_ms=0,
                speech_segments=0,
                gate_backend="silero_vad",
            )

        if not self.available:
            return SileroVadDecision(
                should_transcribe=True,
                reason="vad_unavailable_fallback_allow",
                rms=rms,
                speech_duration_ms=0,
                speech_segments=0,
                gate_backend="rms_only",
            )

        if self.sample_rate not in {8000, 16000}:
            return SileroVadDecision(
                should_transcribe=True,
                reason="vad_sample_rate_unsupported_fallback_allow",
                rms=rms,
                speech_duration_ms=0,
                speech_segments=0,
                gate_backend="rms_only",
            )

        try:
            audio_tensor = self._pcm_to_tensor(pcm_bytes)
            speech_timestamps = self._get_speech_timestamps(
                audio_tensor,
                self._model,
                sampling_rate=self.sample_rate,
                threshold=self.threshold,
                min_silence_duration_ms=self.min_silence_duration_ms,
                speech_pad_ms=self.speech_pad_ms,
            )
        except Exception:
            return SileroVadDecision(
                should_transcribe=True,
                reason="vad_runtime_error_fallback_allow",
                rms=rms,
                speech_duration_ms=0,
                speech_segments=0,
                gate_backend="rms_only",
            )

        speech_segments = len(speech_timestamps)
        speech_samples = 0

        for item in speech_timestamps:
            start = int(item.get("start", 0) or 0)
            end = int(item.get("end", 0) or 0)
            if end > start:
                speech_samples += end - start

        speech_duration_ms = int((speech_samples / float(self.sample_rate)) * 1000.0)

        if speech_segments < self.min_speech_segments:
            return SileroVadDecision(
                should_transcribe=False,
                reason="silence_gate_vad_segments",
                rms=rms,
                speech_duration_ms=speech_duration_ms,
                speech_segments=speech_segments,
                gate_backend="silero_vad",
            )

        if speech_duration_ms < self.min_speech_duration_ms:
            return SileroVadDecision(
                should_transcribe=False,
                reason="silence_gate_vad_duration",
                rms=rms,
                speech_duration_ms=speech_duration_ms,
                speech_segments=speech_segments,
                gate_backend="silero_vad",
            )

        return SileroVadDecision(
            should_transcribe=True,
            reason="speech_detected",
            rms=rms,
            speech_duration_ms=speech_duration_ms,
            speech_segments=speech_segments,
            gate_backend="silero_vad",
        )