from __future__ import annotations

import audioop
import tempfile
import wave
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

from .streaming_chunk_buffer import PCMBufferConfig, PCMChunkBuffer
from .streaming_config import InputFeedStreamingConfig
from .streaming_runtime_debug import build_streaming_debug_payload
from .streaming_types import StreamingChunkResult, StreamingEmit


class WhisperStreamAdapter:
    def __init__(
        self,
        *,
        model: WhisperModel,
        language: str,
        beam_size: int,
        vad_filter: bool,
        config: InputFeedStreamingConfig,
    ) -> None:
        self.model = model
        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.config = config

        self._buffer: PCMChunkBuffer | None = None
        self._last_candidate_text = ""
        self._stable_counter = 0
        self._last_emitted_text = ""

    def _ensure_buffer(self, chunk: StreamingChunkResult) -> None:
        if self._buffer is not None:
            return

        self._buffer = PCMChunkBuffer(
            PCMBufferConfig(
                sample_rate=chunk.sample_rate,
                channels=chunk.channels,
                sample_width=chunk.sample_width,
                max_buffer_seconds=self.config.max_buffer_seconds,
            )
        )

    def _write_wav_file(
        self,
        *,
        path: Path,
        pcm_bytes: bytes,
        sample_rate: int,
        channels: int,
        sample_width: int,
    ) -> None:
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)

    def _transcribe_buffer(self, chunk: StreamingChunkResult, pcm_bytes: bytes) -> tuple[str, int]:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = Path(tmp.name)

        try:
            self._write_wav_file(
                path=wav_path,
                pcm_bytes=pcm_bytes,
                sample_rate=chunk.sample_rate,
                channels=chunk.channels,
                sample_width=chunk.sample_width,
            )
            segments, _info = self.model.transcribe(
                str(wav_path),
                language=self.language,
                vad_filter=self.vad_filter,
                beam_size=self.beam_size,
                condition_on_previous_text=False,
                word_timestamps=True,
            )
            texts: list[str] = []
            speech_segments = 0
            for segment in segments:
                seg_text = str(segment.text or "").strip()
                if not seg_text:
                    continue
                texts.append(seg_text)
                speech_segments += 1

            if self.config.recent_segment_count > 0:
                texts = texts[-self.config.recent_segment_count :]

            return " ".join(texts).strip(), speech_segments
        finally:
            if wav_path.exists():
                wav_path.unlink()

    def feed_chunk_result(self, chunk: StreamingChunkResult) -> tuple[list[StreamingEmit], dict[str, Any]]:
        self._ensure_buffer(chunk)
        assert self._buffer is not None

        self._buffer.append(chunk.pcm_bytes)
        buffer_pcm = self._buffer.get_pcm()

        candidate_text, speech_segments = self._transcribe_buffer(chunk, buffer_pcm)

        if candidate_text and candidate_text == self._last_candidate_text:
            self._stable_counter += 1
        else:
            self._last_candidate_text = candidate_text
            self._stable_counter = 1 if candidate_text else 0

        emits: list[StreamingEmit] = []

        if (
            candidate_text
            and self._stable_counter >= self.config.commit_stable_passes
            and candidate_text != self._last_emitted_text
        ):
            rms = int(audioop.rms(chunk.pcm_bytes, chunk.sample_width)) if chunk.pcm_bytes else 0
            speech_duration_ms = int(self.config.step_seconds * 1000)
            emits.append(
                StreamingEmit(
                    text=candidate_text,
                    rms=rms,
                    speech_duration_ms=speech_duration_ms,
                    speech_segments=speech_segments,
                    gate_backend="whisper_stream_adapter",
                    metadata={
                        **chunk.metadata,
                        "streaming_mode": True,
                    },
                )
            )
            self._last_emitted_text = candidate_text

        buffer_seconds = 0.0
        if self._buffer.bytes_per_second > 0:
            buffer_seconds = len(buffer_pcm) / float(self._buffer.bytes_per_second)

        debug_payload = build_streaming_debug_payload(
            enabled=self.config.enabled,
            last_partial_text=candidate_text,
            stable_counter=self._stable_counter,
            buffer_seconds=buffer_seconds,
        )
        return emits, debug_payload