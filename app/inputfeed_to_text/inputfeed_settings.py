from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parent
APP_DIR = MODULE_DIR.parent
PROJECT_ROOT = APP_DIR.parent

RUNTIME_DIR = PROJECT_ROOT / "runtime"
RUNTIME_SACRED_DIR = RUNTIME_DIR / "sacred"
RUNTIME_STATUS_DIR = RUNTIME_DIR / "status"
RUNTIME_ARCHIVE_DIR = RUNTIME_DIR / "stt_archive"

# RAW transcript (nuevo oficial)
LIVE_TRANSCRIPT_RAW_JSONL = RUNTIME_SACRED_DIR / "live_transcript_raw.jsonl"
LIVE_TRANSCRIPT_RAW_LATEST_JSON = RUNTIME_SACRED_DIR / "live_transcript_raw_latest.json"

# Compatibilidad con nombres viejos
LIVE_TRANSCRIPT_HISTORY_JSONL = RUNTIME_SACRED_DIR / "live_transcript_history.jsonl"
LIVE_TRANSCRIPT_LATEST_JSON = RUNTIME_SACRED_DIR / "live_transcript_latest.json"

# ASSEMBLED transcript
LIVE_TRANSCRIPT_ASSEMBLED_JSONL = RUNTIME_SACRED_DIR / "live_transcript_assembled.jsonl"
LIVE_TRANSCRIPT_ASSEMBLED_LATEST_JSON = RUNTIME_SACRED_DIR / "live_transcript_assembled_latest.json"

INPUTFEED_TO_TEXT_STATUS_JSON = RUNTIME_STATUS_DIR / "inputfeed_to_text_status.json"
ASSEMBLED_TRANSCRIPT_STATUS_JSON = RUNTIME_STATUS_DIR / "assembled_transcript_builder_status.json"

TRANSCRIPT_SESSION_ID = os.getenv(
    "TRANSCRIPT_SESSION_ID",
    time.strftime("session_%Y%m%d_%H%M%S"),
)

TRANSCRIPT_SOURCE_NAME = os.getenv("TRANSCRIPT_SOURCE_NAME", "audio_input").strip() or "audio_input"
TRANSCRIPT_SOURCE_TYPE = os.getenv("TRANSCRIPT_SOURCE_TYPE", "audio_stream").strip() or "audio_stream"

INPUTFEED_SAMPLE_RATE = int(os.getenv("INPUTFEED_SAMPLE_RATE", "16000"))
INPUTFEED_CHANNELS = int(os.getenv("INPUTFEED_CHANNELS", "1"))
INPUTFEED_SAMPLE_WIDTH = 2

INPUTFEED_FRAMES_PER_BUFFER = int(os.getenv("INPUTFEED_FRAMES_PER_BUFFER", "1024"))
INPUTFEED_INPUT_GAIN = float(os.getenv("INPUTFEED_INPUT_GAIN", "1.2"))

WINDOWS_MIC_DEVICE_NAME = os.getenv("WINDOWS_MIC_DEVICE_NAME", "AudioPro X5").strip()
_DEFAULT_SOURCE_BACKEND = "windows_wasapi_mic" if os.name == "nt" else "sounddevice_mic"
INPUTFEED_SOURCE_BACKEND = os.getenv("INPUTFEED_SOURCE_BACKEND", _DEFAULT_SOURCE_BACKEND).strip() or _DEFAULT_SOURCE_BACKEND

INPUTFEED_ENABLE_RNNOISE = os.getenv("INPUTFEED_ENABLE_RNNOISE", "1").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

INPUTFEED_STT_BACKEND = os.getenv("INPUTFEED_STT_BACKEND", "moonshine").strip().lower() or "moonshine"

STT_MODEL = os.getenv("STT_MODEL", "medium").strip() or "medium"
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en").strip() or "en"
STT_COMPUTE_TYPE = os.getenv("STT_COMPUTE_TYPE", "int8").strip() or "int8"
STT_BEAM_SIZE = int(os.getenv("STT_BEAM_SIZE", "3"))

STT_CHUNK_MS = int(os.getenv("STT_CHUNK_MS", "1200"))
INPUTFEED_CHUNK_SECONDS = max(STT_CHUNK_MS, 250) / 1000.0

STT_VAD_FILTER = os.getenv("STT_VAD_FILTER", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

INPUTFEED_DEDUP_SECONDS = max(float(os.getenv("INPUTFEED_DEDUP_SECONDS", "4")), 0.5)

INPUTFEED_ENABLE_SILERO_VAD = os.getenv("INPUTFEED_ENABLE_SILERO_VAD", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

INPUTFEED_MIN_RMS = max(int(os.getenv("INPUTFEED_MIN_RMS", "70")), 40)
INPUTFEED_SILERO_THRESHOLD = min(max(float(os.getenv("INPUTFEED_SILERO_THRESHOLD", "0.50")), 0.20), 0.95)
INPUTFEED_SILERO_MIN_SILENCE_MS = int(os.getenv("INPUTFEED_SILERO_MIN_SILENCE_MS", "250"))
INPUTFEED_SILERO_SPEECH_PAD_MS = int(os.getenv("INPUTFEED_SILERO_SPEECH_PAD_MS", "80"))
INPUTFEED_SILERO_MIN_SPEECH_MS = max(int(os.getenv("INPUTFEED_SILERO_MIN_SPEECH_MS", "300")), 120)
INPUTFEED_SILERO_MIN_SEGMENTS = max(int(os.getenv("INPUTFEED_SILERO_MIN_SEGMENTS", "1")), 1)

INPUTFEED_USE_STREAMING = os.getenv("INPUTFEED_USE_STREAMING", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

INPUTFEED_STREAM_STEP_SECONDS = max(float(os.getenv("INPUTFEED_STREAM_STEP_SECONDS", "1.2")), 0.25)
INPUTFEED_STREAM_OVERLAP_SECONDS = max(float(os.getenv("INPUTFEED_STREAM_OVERLAP_SECONDS", "0.30")), 0.0)
INPUTFEED_STREAM_MAX_BUFFER_SECONDS = max(float(os.getenv("INPUTFEED_STREAM_MAX_BUFFER_SECONDS", "4.0")), 2.0)
INPUTFEED_STREAM_COMMIT_STABLE_PASSES = max(int(os.getenv("INPUTFEED_STREAM_COMMIT_STABLE_PASSES", "2")), 1)
INPUTFEED_STREAM_RECENT_SEGMENT_COUNT = max(int(os.getenv("INPUTFEED_STREAM_RECENT_SEGMENT_COUNT", "2")), 1)

ASSEMBLER_MERGE_WINDOW_SECONDS = max(float(os.getenv("ASSEMBLER_MERGE_WINDOW_SECONDS", "2.2")), 0.1)
ASSEMBLER_FLUSH_IDLE_SECONDS = max(float(os.getenv("ASSEMBLER_FLUSH_IDLE_SECONDS", "1.0")), 0.1)
ASSEMBLER_MAX_BUFFER_PARTS = max(int(os.getenv("ASSEMBLER_MAX_BUFFER_PARTS", "6")), 1)


@dataclass(slots=True)
class InputFeedSettingsSnapshot:
    inputfeed_stt_backend: str
    stt_model: str
    stt_language: str


def build_inputfeed_settings_snapshot() -> InputFeedSettingsSnapshot:
    return InputFeedSettingsSnapshot(
        inputfeed_stt_backend=INPUTFEED_STT_BACKEND,
        stt_model=STT_MODEL,
        stt_language=STT_LANGUAGE,
    )
