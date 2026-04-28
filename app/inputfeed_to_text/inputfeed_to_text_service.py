from __future__ import annotations

import time
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from faster_whisper import WhisperModel

from .inputfeed_settings import INPUTFEED_STT_BACKEND
from .mic_audio_source import create_mic_audio_source
from .providers.moonshine.moonshine_stt_provider import MoonshineSTTProvider
from .source_config import (
    CHUNK_SECONDS,
    INPUT_CHANNELS,
    INPUT_SAMPLE_RATE,
    INPUTFEED_DEDUP_SECONDS,
    INPUTFEED_ENABLE_SILERO_VAD,
    INPUTFEED_MIN_RMS,
    INPUTFEED_SILERO_MIN_SEGMENTS,
    INPUTFEED_SILERO_MIN_SPEECH_MS,
    INPUTFEED_SILERO_MIN_SILENCE_MS,
    INPUTFEED_SILERO_SPEECH_PAD_MS,
    INPUTFEED_SILERO_THRESHOLD,
    INPUTFEED_STREAM_COMMIT_STABLE_PASSES,
    INPUTFEED_STREAM_MAX_BUFFER_SECONDS,
    INPUTFEED_STREAM_OVERLAP_SECONDS,
    INPUTFEED_STREAM_RECENT_SEGMENT_COUNT,
    INPUTFEED_STREAM_STEP_SECONDS,
    INPUTFEED_USE_STREAMING,
    SAMPLE_WIDTH,
    SESSION_ID,
    SOURCE_NAME,
    SOURCE_TYPE,
    STT_BEAM_SIZE,
    STT_COMPUTE_TYPE,
    STT_LANGUAGE,
    STT_MODEL,
    STT_VAD_FILTER,
)
from .streaming import (
    InputFeedStreamingConfig,
    StreamingChunkResult,
    WhisperStreamAdapter,
)
from .transcript_runtime import (
    append_raw_transcript_line,
    archive_and_reset_live_transcript,
    write_inputfeed_status,
)
from .vad.silero_vad_gate import SileroVadGate


class AudioChunkSource(Protocol):
    def read_chunk(self, chunk_seconds: float) -> bytes: ...
    def close(self) -> None: ...


def _extract_rnnoise_meta(metadata: dict[str, object]) -> dict[str, object]:
    return {
        "rnnoise_enabled": bool(metadata.get("rnnoise_enabled", False)),
        "rnnoise_available": bool(metadata.get("rnnoise_available", False)),
        "rnnoise_active": bool(metadata.get("rnnoise_active", False)),
        "rnnoise_backend": str(metadata.get("rnnoise_backend", "")),
        "rnnoise_error": str(metadata.get("rnnoise_error", "")),
        "rnnoise_speech_prob_mean": float(metadata.get("rnnoise_speech_prob_mean", 0.0) or 0.0),
        "rnnoise_raw_rms": int(metadata.get("rnnoise_raw_rms", 0) or 0),
        "rnnoise_denoised_rms": int(metadata.get("rnnoise_denoised_rms", 0) or 0),
    }


@dataclass(slots=True)
class TranscriptChunk:
    pcm_bytes: bytes
    chunk_seconds: float


def _write_wav_file(path: Path, pcm_bytes: bytes) -> None:
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(INPUT_CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(INPUT_SAMPLE_RATE)
        wav_file.writeframes(pcm_bytes)


def _transcribe_chunk(model: WhisperModel, chunk: TranscriptChunk) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = Path(tmp.name)

    try:
        _write_wav_file(wav_path, chunk.pcm_bytes)
        segments, _info = model.transcribe(
            str(wav_path),
            language=STT_LANGUAGE,
            vad_filter=STT_VAD_FILTER,
            beam_size=STT_BEAM_SIZE,
            condition_on_previous_text=False,
            word_timestamps=True,
        )
        text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())
        return text.strip()
    finally:
        if wav_path.exists():
            wav_path.unlink()


class InputFeedToTextService:
    def __init__(self, audio_source: AudioChunkSource) -> None:
        self.audio_source = audio_source
        self.model = WhisperModel(
            STT_MODEL,
            device="cpu",
            compute_type=STT_COMPUTE_TYPE,
        )
        self.session_id = SESSION_ID
        self._running = False
        self._last_written_text = ""
        self._last_written_ts = 0.0

        self._vad_gate = SileroVadGate(
            sample_rate=INPUT_SAMPLE_RATE,
            sample_width=SAMPLE_WIDTH,
            min_rms=INPUTFEED_MIN_RMS,
            min_speech_duration_ms=INPUTFEED_SILERO_MIN_SPEECH_MS,
            min_speech_segments=INPUTFEED_SILERO_MIN_SEGMENTS,
            threshold=INPUTFEED_SILERO_THRESHOLD,
            min_silence_duration_ms=INPUTFEED_SILERO_MIN_SILENCE_MS,
            speech_pad_ms=INPUTFEED_SILERO_SPEECH_PAD_MS,
        )

        self._stream_adapter = WhisperStreamAdapter(
            model=self.model,
            language=STT_LANGUAGE,
            beam_size=STT_BEAM_SIZE,
            vad_filter=STT_VAD_FILTER,
            config=InputFeedStreamingConfig(
                enabled=INPUTFEED_USE_STREAMING,
                step_seconds=INPUTFEED_STREAM_STEP_SECONDS,
                overlap_seconds=INPUTFEED_STREAM_OVERLAP_SECONDS,
                max_buffer_seconds=INPUTFEED_STREAM_MAX_BUFFER_SECONDS,
                commit_stable_passes=INPUTFEED_STREAM_COMMIT_STABLE_PASSES,
                recent_segment_count=INPUTFEED_STREAM_RECENT_SEGMENT_COUNT,
            ),
        )

    def _maybe_write_record(
        self,
        *,
        text: str,
        rms: int,
        speech_duration_ms: int,
        speech_segments: int,
        gate_backend: str,
        rnnoise_meta: dict[str, object],
        extra_meta: dict[str, object] | None = None,
    ) -> None:
        if not text:
            return

        now_ts = time.time()
        if text == self._last_written_text and (now_ts - self._last_written_ts) < INPUTFEED_DEDUP_SECONDS:
            write_inputfeed_status(
                "running",
                session_id=self.session_id,
                source=SOURCE_NAME,
                stt_backend="whisper",
                last_event="dedup_text",
                last_text=text,
                last_rms=rms,
                dedup_seconds=INPUTFEED_DEDUP_SECONDS,
                speech_duration_ms=speech_duration_ms,
                speech_segments=speech_segments,
                gate_backend=gate_backend,
                **rnnoise_meta,
            )
            return

        metadata = {
            "model_name": STT_MODEL,
            "chunk_seconds": CHUNK_SECONDS,
            "source_type": SOURCE_TYPE,
            "rms": rms,
            "speech_duration_ms": speech_duration_ms,
            "speech_segments": speech_segments,
            "gate_backend": gate_backend,
            "rnnoise_active": bool(rnnoise_meta.get("rnnoise_active", False)),
            "rnnoise_backend": str(rnnoise_meta.get("rnnoise_backend", "")),
            "rnnoise_speech_prob_mean": float(rnnoise_meta.get("rnnoise_speech_prob_mean", 0.0) or 0.0),
            "stt_backend": "whisper",
        }
        if extra_meta:
            metadata.update(extra_meta)

        record = append_raw_transcript_line(
            source=SOURCE_NAME,
            session_id=self.session_id,
            text=text,
            language=STT_LANGUAGE,
            metadata=metadata,
        )

        self._last_written_text = record["text"]
        self._last_written_ts = float(record["ts"] or now_ts)

        write_inputfeed_status(
            "running",
            session_id=self.session_id,
            source=SOURCE_NAME,
            language=STT_LANGUAGE,
            chunk_seconds=CHUNK_SECONDS,
            stt_backend="whisper",
            last_event="transcript_written",
            last_event_id=record["event_id"],
            last_text=record["text"],
            last_rms=rms,
            min_rms=INPUTFEED_MIN_RMS,
            speech_duration_ms=speech_duration_ms,
            speech_segments=speech_segments,
            gate_backend=gate_backend,
            **rnnoise_meta,
        )

    def run_forever(self) -> None:
        if INPUTFEED_STT_BACKEND == "moonshine":
            provider = MoonshineSTTProvider()
            provider.run_forever()
            return

        self._running = True

        write_inputfeed_status(
            "starting",
            session_id=self.session_id,
            source=SOURCE_NAME,
            source_type=SOURCE_TYPE,
            language=STT_LANGUAGE,
            chunk_seconds=CHUNK_SECONDS,
            model=STT_MODEL,
            compute_type=STT_COMPUTE_TYPE,
            stt_backend="whisper",
            silero_vad_enabled=INPUTFEED_ENABLE_SILERO_VAD,
            silero_vad_available=self._vad_gate.available,
            silero_vad_load_error=self._vad_gate.load_error,
            min_rms=INPUTFEED_MIN_RMS,
            silero_threshold=INPUTFEED_SILERO_THRESHOLD,
            silero_min_speech_ms=INPUTFEED_SILERO_MIN_SPEECH_MS,
            silero_min_segments=INPUTFEED_SILERO_MIN_SEGMENTS,
            dedup_seconds=INPUTFEED_DEDUP_SECONDS,
            streaming_enabled=INPUTFEED_USE_STREAMING,
        )

        try:
            write_inputfeed_status(
                "running",
                session_id=self.session_id,
                source=SOURCE_NAME,
                source_type=SOURCE_TYPE,
                language=STT_LANGUAGE,
                chunk_seconds=CHUNK_SECONDS,
                stt_backend="whisper",
                silero_vad_enabled=INPUTFEED_ENABLE_SILERO_VAD,
                silero_vad_available=self._vad_gate.available,
                min_rms=INPUTFEED_MIN_RMS,
                silero_threshold=INPUTFEED_SILERO_THRESHOLD,
                silero_min_speech_ms=INPUTFEED_SILERO_MIN_SPEECH_MS,
                silero_min_segments=INPUTFEED_SILERO_MIN_SEGMENTS,
                dedup_seconds=INPUTFEED_DEDUP_SECONDS,
                streaming_enabled=INPUTFEED_USE_STREAMING,
            )

            while self._running:
                source_metadata: dict[str, object] = {}
                if hasattr(self.audio_source, "read_chunk_result"):
                    chunk_result = self.audio_source.read_chunk_result(CHUNK_SECONDS)  # type: ignore[attr-defined]
                    pcm_bytes = chunk_result.pcm_bytes
                    source_metadata = chunk_result.metadata if isinstance(chunk_result.metadata, dict) else {}
                else:
                    pcm_bytes = self.audio_source.read_chunk(CHUNK_SECONDS)

                rnnoise_meta = _extract_rnnoise_meta(source_metadata)

                if not pcm_bytes:
                    write_inputfeed_status(
                        "running",
                        session_id=self.session_id,
                        source=SOURCE_NAME,
                        stt_backend="whisper",
                        last_event="empty_chunk",
                        **rnnoise_meta,
                    )
                    continue

                if INPUTFEED_USE_STREAMING:
                    vad_decision = self._vad_gate.decide(pcm_bytes)

                    if INPUTFEED_ENABLE_SILERO_VAD and not vad_decision.should_transcribe:
                        write_inputfeed_status(
                            "running",
                            session_id=self.session_id,
                            source=SOURCE_NAME,
                            stt_backend="whisper",
                            last_event=vad_decision.reason,
                            last_rms=vad_decision.rms,
                            min_rms=INPUTFEED_MIN_RMS,
                            speech_duration_ms=vad_decision.speech_duration_ms,
                            speech_segments=vad_decision.speech_segments,
                            gate_backend=vad_decision.gate_backend,
                            **rnnoise_meta,
                        )
                        continue

                    if not INPUTFEED_ENABLE_SILERO_VAD and vad_decision.rms < INPUTFEED_MIN_RMS:
                        write_inputfeed_status(
                            "running",
                            session_id=self.session_id,
                            source=SOURCE_NAME,
                            stt_backend="whisper",
                            last_event="silence_gate_rms",
                            last_rms=vad_decision.rms,
                            min_rms=INPUTFEED_MIN_RMS,
                            gate_backend="rms_only",
                            **rnnoise_meta,
                        )
                        continue

                    stream_chunk = StreamingChunkResult(
                        pcm_bytes=pcm_bytes,
                        sample_rate=INPUT_SAMPLE_RATE,
                        channels=INPUT_CHANNELS,
                        sample_width=SAMPLE_WIDTH,
                        metadata=source_metadata,
                    )
                    emits, stream_debug = self._stream_adapter.feed_chunk_result(stream_chunk)

                    if not emits:
                        write_inputfeed_status(
                            "running",
                            session_id=self.session_id,
                            source=SOURCE_NAME,
                            stt_backend="whisper",
                            last_event="streaming_waiting_commit",
                            **stream_debug,
                            **rnnoise_meta,
                        )
                        continue

                    for emit in emits:
                        self._maybe_write_record(
                            text=emit.text,
                            rms=emit.rms,
                            speech_duration_ms=emit.speech_duration_ms,
                            speech_segments=emit.speech_segments,
                            gate_backend=emit.gate_backend,
                            rnnoise_meta=rnnoise_meta,
                            extra_meta={"streaming_mode": True},
                        )
                    continue

                vad_decision = self._vad_gate.decide(pcm_bytes)
                if INPUTFEED_ENABLE_SILERO_VAD and not vad_decision.should_transcribe:
                    write_inputfeed_status(
                        "running",
                        session_id=self.session_id,
                        source=SOURCE_NAME,
                        stt_backend="whisper",
                        last_event=vad_decision.reason,
                        last_rms=vad_decision.rms,
                        min_rms=INPUTFEED_MIN_RMS,
                        speech_duration_ms=vad_decision.speech_duration_ms,
                        speech_segments=vad_decision.speech_segments,
                        gate_backend=vad_decision.gate_backend,
                        **rnnoise_meta,
                    )
                    continue

                rms = vad_decision.rms
                gate_backend = vad_decision.gate_backend if INPUTFEED_ENABLE_SILERO_VAD else "rms_only"
                speech_duration_ms = vad_decision.speech_duration_ms if INPUTFEED_ENABLE_SILERO_VAD else 0
                speech_segments = vad_decision.speech_segments if INPUTFEED_ENABLE_SILERO_VAD else 0

                if not INPUTFEED_ENABLE_SILERO_VAD and rms < INPUTFEED_MIN_RMS:
                    write_inputfeed_status(
                        "running",
                        session_id=self.session_id,
                        source=SOURCE_NAME,
                        stt_backend="whisper",
                        last_event="silence_gate_rms",
                        last_rms=rms,
                        min_rms=INPUTFEED_MIN_RMS,
                        gate_backend=gate_backend,
                        **rnnoise_meta,
                    )
                    continue

                chunk = TranscriptChunk(pcm_bytes=pcm_bytes, chunk_seconds=CHUNK_SECONDS)
                text = _transcribe_chunk(self.model, chunk)

                if not text:
                    write_inputfeed_status(
                        "running",
                        session_id=self.session_id,
                        source=SOURCE_NAME,
                        stt_backend="whisper",
                        last_event="empty_text",
                        last_rms=rms,
                        min_rms=INPUTFEED_MIN_RMS,
                        speech_duration_ms=speech_duration_ms,
                        speech_segments=speech_segments,
                        gate_backend=gate_backend,
                        **rnnoise_meta,
                    )
                    continue

                self._maybe_write_record(
                    text=text,
                    rms=rms,
                    speech_duration_ms=speech_duration_ms,
                    speech_segments=speech_segments,
                    gate_backend=gate_backend,
                    rnnoise_meta=rnnoise_meta,
                    extra_meta={"streaming_mode": False},
                )

        except KeyboardInterrupt:
            write_inputfeed_status(
                "stopped",
                session_id=self.session_id,
                source=SOURCE_NAME,
                stt_backend="whisper",
                reason="keyboard_interrupt",
            )
        except Exception as exc:
            write_inputfeed_status(
                "error",
                session_id=self.session_id,
                source=SOURCE_NAME,
                stt_backend="whisper",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise
        finally:
            try:
                self.audio_source.close()
            except Exception:
                pass

            archive_info = archive_and_reset_live_transcript(session_id=self.session_id)
            write_inputfeed_status(
                "stopped",
                session_id=self.session_id,
                source=SOURCE_NAME,
                stt_backend="whisper",
                archived=bool(archive_info),
                archive_path=archive_info.get("raw_archive_path"),
            )

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    service = InputFeedToTextService(audio_source=create_mic_audio_source())
    service.run_forever()
