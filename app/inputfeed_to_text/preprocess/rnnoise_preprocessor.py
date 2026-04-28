from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class RNNoiseProcessResult:
    pcm_bytes: bytes
    active: bool
    backend: str
    error: str
    speech_prob_mean: float


class RNNoisePreprocessor:
    def __init__(self, *, enabled: bool) -> None:
        self.enabled = bool(enabled)
        self.available = False
        self.load_error = ""
        self._denoiser: Any | None = None

        if not self.enabled:
            return

        try:
            from pyrnnoise import RNNoise  # type: ignore

            self._denoiser = RNNoise(sample_rate=16000)
            self.available = True
        except Exception as exc:
            self._denoiser = None
            self.available = False
            self.load_error = f"{type(exc).__name__}: {exc}"

    def process_pcm_bytes(
        self,
        pcm_bytes: bytes,
        *,
        sample_rate: int,
        channels: int,
        sample_width: int,
    ) -> RNNoiseProcessResult:
        if not self.enabled:
            return RNNoiseProcessResult(
                pcm_bytes=pcm_bytes,
                active=False,
                backend="disabled",
                error="",
                speech_prob_mean=0.0,
            )

        if not self.available or self._denoiser is None:
            return RNNoiseProcessResult(
                pcm_bytes=pcm_bytes,
                active=False,
                backend="fallback_raw",
                error=self.load_error or "rnnoise_unavailable",
                speech_prob_mean=0.0,
            )

        if sample_width != 2:
            return RNNoiseProcessResult(
                pcm_bytes=pcm_bytes,
                active=False,
                backend="fallback_raw",
                error=f"unsupported_sample_width:{sample_width}",
                speech_prob_mean=0.0,
            )

        if not pcm_bytes:
            return RNNoiseProcessResult(
                pcm_bytes=pcm_bytes,
                active=True,
                backend="rnnoise",
                error="",
                speech_prob_mean=0.0,
            )

        try:
            mono_samples = np.frombuffer(pcm_bytes, dtype=np.int16)
            if channels > 1:
                frame_count = len(mono_samples) // channels
                if frame_count <= 0:
                    return RNNoiseProcessResult(
                        pcm_bytes=pcm_bytes,
                        active=False,
                        backend="fallback_raw",
                        error="invalid_channel_frame_count",
                        speech_prob_mean=0.0,
                    )
                mono_samples = mono_samples[: frame_count * channels]
                channel_major = mono_samples.reshape(frame_count, channels).T
            else:
                channel_major = np.atleast_2d(mono_samples)

            denoised_frames: list[np.ndarray] = []
            speech_scores: list[float] = []
            for speech_prob, denoised in self._denoiser.denoise_chunk(channel_major, partial=True):
                denoised_frames.append(denoised)
                try:
                    speech_scores.append(float(np.mean(speech_prob)))
                except Exception:
                    pass

            if not denoised_frames:
                return RNNoiseProcessResult(
                    pcm_bytes=pcm_bytes,
                    active=False,
                    backend="fallback_raw",
                    error="no_denoised_frames",
                    speech_prob_mean=0.0,
                )

            denoised = np.concatenate(denoised_frames, axis=1)
            denoised = np.clip(denoised, -32768, 32767).astype(np.int16)
            if channels > 1:
                interleaved = denoised.T.reshape(-1)
            else:
                interleaved = denoised.reshape(-1)

            return RNNoiseProcessResult(
                pcm_bytes=interleaved.tobytes(),
                active=True,
                backend="rnnoise",
                error="",
                speech_prob_mean=float(np.mean(speech_scores)) if speech_scores else 0.0,
            )
        except Exception as exc:
            return RNNoiseProcessResult(
                pcm_bytes=pcm_bytes,
                active=False,
                backend="fallback_raw",
                error=f"{type(exc).__name__}: {exc}",
                speech_prob_mean=0.0,
            )
